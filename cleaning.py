import re
import psycopg2
from db import Database

def getCaptions():
    captions = []

    # SQL query to get newly added captions
    SQL = "SELECT id, url, caption \
           FROM posts \
           WHERE caption <> 'Caption does not exist.' \
           AND NOT EXISTS (SELECT post_id \
                           FROM cleaned_captions \
                           WHERE posts.id = cleaned_captions.post_id);"
    
    with Database() as db:
        db.set_session(commit=True)
        try:
            db.execute(SQL)
        except psycopg2.Error as e:
            print('ERROR: getCaptions query unsuccessful.')
            print(e)

        captions = db.fetchall()
        captions = [list(record) for record in captions]
    return captions

def balance(caption):
    if "'" in caption or "’" in caption:
        caption = caption.replace("'", "''")
        caption = caption.replace("’", "''")
    return caption

def transformAndLoad(captions):
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

                with Database() as db:
                    db.set_session(commit=True)
                    try:
                        db.execute(SQL.format(url, cleanCaption, postID))
                        print('^ SUCCESS: Record Inserted. ^')
                    except psycopg2.Error as e:
                        print('^ ERROR: Record insertion unssuccessful. ^')
                        print(e)


if __name__ == '__main__':
    captions = getCaptions()
    transformAndLoad(captions)

