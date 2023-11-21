import base64
import psycopg2
import requests
import config as cfg
from db import Database
from datetime import date
from urllib.parse import urlencode
from flask import Flask, request, session, redirect

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
    
    return redirect('/sleepingongems')


@app.route('/sleepingongems')
def addSongs():
    # Get the songs that need to be added from the Cleaned_Captions table
    with Database() as db:
        db.set_session(commit=True)
        SQL = "SELECT id, clean_caption \
               FROM cleaned_captions \
               WHERE NOT EXISTS(SELECT cc_id \
                                FROM playlist \
                                WHERE cleaned_captions.id = playlist.cc_id);"
        
        try:
            db.execute(SQL)
        except psycopg2.Error as e:
            print('ERROR: SQL query execution falied.')
            print(e)

        songsToAdd = db.fetchall()
        songsToAdd = [list(record) for record in songsToAdd]
    print(songsToAdd)  
    
    # Create endpoint and headers to search and add songs to playlist
    endpoint = f'https://api.spotify.com/v1/playlists/{cfg.playlistID}/tracks'
    reqHeaders = {
        'Authorization' : 'Bearer ' + session['access_token'],
        'Content-Type' : 'application/json'
    }
    
    searchHeaders = {
        'Authorization' : 'Bearer ' + session['access_token']
    }

    # Beginning of playlist logic
    while songsToAdd:
        # Get the URIs of the first 100 songs 
        uris = []
        addToPlaylist = songsToAdd[:100]
        
        # Iterate through first 100 songs and obtain track info through the search endpoint
        for song in addToPlaylist:
            # Search for current song using search endpoint
            searchEndpoint = 'https://api.spotify.com/v1/search?' + f'q={song[1]}&type=track&limit=1'

            res = requests.get(searchEndpoint, headers=searchHeaders)
            res = res.json()

            # Collect information needed, if no information can be collected continue 
            try:
                songID = res['tracks']['items'][0]['id']
                songURI = res['tracks']['items'][0]['uri']
                songName = res['tracks']['items'][0]['name']
                songArtists = []
                for artist in res['tracks']['items'][0]['artists']:
                    songArtists.append(artist['name'])
                addedAt = date.today()
                ccID = song[0]
            except:
                print(f'WARNING: Unable to search {song[1]}.')
                continue
            
            # Insert song into 'playlist' table in database
            with Database() as db:
                db.set_session(commit=True)

                SQL = "INSERT INTO playlist VALUES(%s, %s, %s, %s, %s, %s)"
                try:
                    db.execute(SQL, [songID, songURI, songName, songArtists, addedAt, ccID])
                    print(f'SUCCESS: {songName} added to playlist.')
                except psycopg2.Error as e:
                    print(f'ERROR: Record insertion for {songName} failed.')
                    print(e)
                    continue
            
            # Add URI to list– will be added if information is collected and does not exist in table
            uris.append(songURI)
    
        # Send post request with the URIs to add songs to playlist
        reqBody = {
            'uris' : uris
        }
        res = requests.post(endpoint, headers=reqHeaders, json=reqBody)

        # Delete the first 100 items
        songsToAdd = songsToAdd[100:]

    return 'Success'

if __name__ == '__main__':
    app.run(port=3000, debug=True)