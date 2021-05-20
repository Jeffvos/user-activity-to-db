import datetime
import psycopg2
from config import config as APPCONFIG
from queries import queries
APPCONFIG = APPCONFIG()
QUERIES = queries()


class Client:
    def __init__(self):
        HOST = APPCONFIG['psql']['host']
        PORT = APPCONFIG['psql']['port']
        DATABASE = APPCONFIG['psql']['database']
        USER = APPCONFIG['psql']['user']
        PASSWORD = APPCONFIG['psql']['password']

        self.conn = psycopg2.connect(
        host = HOST,
        port = PORT,
        database = DATABASE,
        user = USER,
        password = PASSWORD
        )
        self.cur = self.conn.cursor()

    def insert_new(self, userblock):
        user_id = userblock['jiraId']
        username = userblock['username'].encode("utf-8")
        full_name = userblock['fullName'].encode("utf-8")
        if "'" in full_name:
            full_name=full_name.replace("'"," ")
        email = userblock['email'].encode("utf-8")
        account_last_login = userblock['lastLogin'].encode("utf-8")

        try:
            account_last_login = datetime.datetime.strptime(account_last_login, "%Y-%m-%d %H:%M")
        except ValueError:
            account_last_login = datetime.datetime.strptime("1900-01-01 12:00", "%Y-%m-%d %H:%M")

        if self.check_if_exists(user_id) is True:
            self.update_existing(user_id, account_last_login)
        else:
            try:
                try:
                    self.cur.execute(QUERIES['insert'].format(user_id, username, account_last_login, full_name, email))
                except UnicodeDecodeError:
                    full_name = username
                    self.cur.execute(QUERIES['insert'].format(user_id, username, account_last_login, full_name, email))
                
                self.conn.commit()

            except psycopg2.Error as e:
                self.conn.rollback()
                error = str(e)
                
                if 'duplicate' in error:
                    self.cur.execute(QUERIES['update'].format(account_last_login, user_id))
                    self.conn.commit()
                else:
                    print(error)

    def update_existing(self, user_id, account_last_login):
        self.cur.execute(QUERIES['update'].format(account_last_login, user_id))
        self.conn.commit()

    def check_if_exists(self, user_id):
        try:
            self.cur.execute(QUERIES['find'].format(user_id))
            if True in self.cur.fetchone():
                return True
            else:
                return False
        except psycopg2.Error as e:
            print(e)

    def check_inactive_user(self, userblock):
        user_id = userblock['jiraId']
        if self.check_if_exists(user_id) is True:
            self.cur.execute(QUERIES['delete'].format(user_id))
            self.conn.commit()
