import re
import time
import json
import base64
import requests
import psycopg2
import itertools
import config as cfg

def connectDB():
    try:
        conn = psycopg2.connect(f'host=localhost dbname=sleepingongems user=postgres password={cfg.dbPassword}')
    except psycopg2.Error as e:
        print('ERROR: Connection to sleepingongems database unsuccessful.')
        print(e)
    
    try:
        cur = conn.cursor()
    except psycopg2.Error as e:
        print('ERROR: Cursor initialization unsuccessful.')
        print(e)

    print('CONNECTED TO DATABASE.')
    return conn, cur

def getCaptions(cur):
    SQL = f'SELECT caption FROM posts WHERE caption <> \'Caption does not exist.\''
    try:
        cur.execute(SQL)
    except psycopg2.Error as e:
        print('ERROR: getCaptions query unsuccessful.')
        print(e)

    captions = cur.fetchall()
    captions = list(itertools.chain(*captions))
    
    return captions

def transform(captions):
    cleaned = []
    for caption in captions:
        if '🎶' in caption:
            pattern = re.compile(r'\b(.+)\s-\s(.+)\b')
            match = pattern.finditer(caption)

            for m in match:
                s = re.sub(r'\(.*?\)|\(.*?\w*|\[.*?\]+/g',"",str(m.group(0)))
                cleaned.append(s)

    return cleaned
            
def getAccessToken():
    authString = cfg.SPOTIFY_CLIENT_ID + ':' + cfg.SPOTIFY_CLIENT_SECRET
    authBytes = authString.encode('utf-8')
    authBase64 = str(base64.b64encode(authBytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization' : 'Basic ' + authBase64,
        'Content-Type' : 'application/x-www-form-urlencoded'
    }
    data = {'grant_type' : 'client_credentials'}
    result = requests.post(url, headers=headers, data=data)
    jsonResult = json.loads(result.content)
    print(jsonResult)
    token = jsonResult['access_token']

    return token

def search(captions, token):
    url = 'https://api.spotify.com/v1/search'
    headers = {
        'Authorization' : 'Bearer ' + token
    }


start = time.time()
conn, cur = connectDB()

captions = getCaptions(cur)
captionsCleaned = transform(captions)

accessToken = getAccessToken()

print(captionsCleaned)
print(accessToken)
print(time.time() - start)
