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

def getCaptions(cur):
    SQL = f'SELECT captions FROM posts WHERE captions != "Caption does not exist."'
    try:
        cur.execute(SQL)
    except psycopg2.Error as e:
        print('ERROR: getCaptions query unsuccessful.')
        print(e)


if __name__ == '__main__':
    cur, conn = connectDB()