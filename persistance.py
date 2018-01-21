import sqlite3
from sqlite3 import Error


class sqlite_persistance:
    def __init__(self):
        try:
            self.conn = sqlite3.connect("rsafactor.db")
            c = self.conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS statistics (method TEXT NOT NULL, bits INT NOT NULL, time BIGINT NOT NULL)")
            self.conn.commit()
        except Error as e:
            print(e)

    def save_statistics(self, results, method):
        c = self.conn.cursor()
        c.executemany("INSERT INTO statistics VALUES (?, ?, ?)", [(method, key, item) for key, value in results.items() for item in value])
        self.conn.commit()

    def close_connection(self):
        self.conn.close()



