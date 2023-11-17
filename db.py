import psycopg2
import config as cfg

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(f'host=localhost 
                                       dbname=sleepingongems 
                                       user=postgres 
                                       password={cfg.dbPassword}')
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    @property
    def connection(self):
        return self.conn
    
    @property
    def cursor(self):
        return self.cur
    
    def close(self):
        self.cur.close()
        self.conn.close()

    def autoCommit(self, commit=True):
        self.conn.set_session(commit)

    

    

    