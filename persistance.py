import sqlite3
from sqlite3 import Error


class sqlite_persistance:
    def __init__(self):
        try:
            conn = sqlite3.connect("rsafactor.db")
            print(sqlite3.version)
        except Error as e:
            print(e)
        finally:
            conn.close()


