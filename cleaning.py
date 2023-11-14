import re
import time
import psycopg2
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

def createTable(cur):
    SQL = 'CREATE TABLE IF NOT EXISTS cleaned_captions (id SERIAL PRIMARY KEY, \
                                                        url VARCHAR(50), \
                                                        clean_caption TEXT, \
                                                        post_id INTEGER REFERENCES posts(id));'
    try:
        cur.execute(SQL)
        print('SUCCESS: Cleaned_Captions table created.')
    except psycopg2.Error as e:
        print('ERROR: Cleaned_Captions table creation unsuccessful.')
        print(e)

def getCaptions(cur):
    SQL = 'SELECT id, url, caption FROM posts WHERE caption <> \'Caption does not exist.\''
    try:
        cur.execute(SQL)
    except psycopg2.Error as e:
        print('ERROR: getCaptions query unsuccessful.')
        print(e)

    captions = cur.fetchall()
    captions = [list(record) for record in captions]
    return captions

def balance(caption):
    if "'" in caption or "’" in caption:
        caption = caption.replace("'", "''")
        caption = caption.replace("’", "''")
    return caption

def transformAndLoad(captions, cur):
    SQL = "INSERT INTO cleaned_captions (url, clean_caption, post_id) VALUES ('{}', '{}', '{}');"
    for caption in captions:
        # Check if caption contains a song (Majority of posts will contain a song if '🎶' exists in the caption)
        if '🎶' in caption[2]:
            postID = caption[0]
            url = caption[1]
            pattern = re.compile(r'\b(.+)\s-\s(.+)\b')
            match = pattern.finditer(caption[2])

            # Find matches of text following the format 'artist/song name - artist/song name'
            for m in match:
                cleanCaption = balance(re.sub(r'\(.*?\)|\(.*?\w*|\[.*?\]+/g',"",str(m.group(0))))
                print('URL: ' + str(url) +
                    '\nCaption: ' + str(cleanCaption) +
                    '\nPost ID: ' + str(postID))

                try:
                    cur.execute(SQL.format(url, cleanCaption, postID))
                    print('^ SUCCESS: Record Inserted. ^')
                except psycopg2.Error as e:
                    print('^ ERROR: Record insertion unssuccessful. ^')
                    print(e)


start = time.time()
conn, cur = connectDB()
conn.set_session(autocommit=True)
createTable(cur)
captions = getCaptions(cur)
transformAndLoad(captions, cur)
print(time.time() - start)
