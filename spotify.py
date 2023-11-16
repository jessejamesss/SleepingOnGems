import base64
import psycopg2
import requests
import config as cfg
from itertools import chain
from urllib.parse import urlencode
from flask import Flask, request, jsonify, session, redirect

app = Flask(__name__)
app.secret_key = cfg.SECRET_KEY
CLIENT_ID = cfg.SPOTIFY_CLIENT_ID
CLIENT_SECRET = cfg.SPOTIFY_CLIENT_SECRET
AUTH_URL = 'https://accounts.spotify.com/authorize?'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

@app.route('/')
def login():
    authRequest = AUTH_URL + urlencode({
        'client_id' : CLIENT_ID,
        'response_type' : 'code',
        'redirect_uri' : 'http://localhost:3000/callback',
        'scope' : 'playlist-modify-public playlist-modify-private',
        'show_dialog' : True
    })
    return redirect(authRequest)

@app.route('/callback')
def callback():
    authString = CLIENT_ID + ':' + CLIENT_SECRET
    authBytes = authString.encode('utf-8')
    authBase64 = str(base64.b64encode(authBytes), 'utf-8')
    authCode = request.args.get('code')
    reqBody = {
        'grant_type' : 'authorization_code',
        'code' : authCode,
        'redirect_uri' : 'http://localhost:3000/callback'
    }
    reqHeaders = {
        'Authorization' : 'Basic ' + authBase64,
        'Content-Type' : 'application/x-www-form-urlencoded'
    }

    res = requests.post(TOKEN_URL, data=reqBody, headers=reqHeaders)
    token_info = res.json()

    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    # session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
    return redirect('/sleepingongems')


@app.route('/sleepingongems')
def addSongs():
    SQL = 'SELECT clean_caption FROM cleaned_captions;'
    endpoint = f'https://api.spotify.com/v1/playlists/{cfg.playlistID}/tracks'
    reqHeaders = {
        'Authorization' : 'Bearer ' + session['access_token'],
        'Content-Type' : 'application/json'
    }

    try:
        conn = psycopg2.connect(f'host=localhost dbname=sleepingongems user=postgres password={cfg.dbPassword}')
    except psycopg2.Error as e:
        print('ERROR: Connection to sleepingongems unsuccessful.')
        print(e)

    try:
        cur = conn.cursor()
    except psycopg2.Error as e:
        print('ERROR: Cursor initialization unsuccessful.')
        print(e)

    try:
        cur.execute(SQL)
    except psycopg2.Error as e:
        print('ERROR: SQL query execution falied.')
        print(e)

    songsToAdd = cur.fetchall()
    songsToAdd = list(chain.from_iterable(songsToAdd))
    print(songsToAdd)
    # for i, song in enumerate(songsToAdd):
    reqBody = {
        'uris': ['spotify:track:4iV5W9uYEdYUVa79Axb7Rh', 'spotify:track:1i1fxkWeaMmKEB4T7zqbzK']
    }
    res = requests.post(endpoint, headers=reqHeaders, json=reqBody)
    return jsonify(res.json())


app.run(port=3000, debug=True)