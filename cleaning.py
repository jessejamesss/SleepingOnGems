import re
import time
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
    hasSymbol = []
    for caption in captions:
        if '🎶' in caption:
            hasSymbol.append(caption)

    return hasSymbol

if __name__ == '__main__':
    start = time.time()
    conn, cur = connectDB()
    captions = getCaptions(cur)

    withMusic = transform(captions)
    for caption in withMusic:
        pattern = re.compile(r'\b(.+)\s-\s(.+)\b')
        match = pattern.finditer(caption)

        for m in match:
            s = re.sub(r'\(.*?\)|\(.*?\w*|\[.*?\]+|@\w+/g',"",str(m.group(0)))
            print(s)


    print(time.time() - start)
