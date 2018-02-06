import sqlite3
from sqlite3 import Error


class sqlite_persistance:
    def __init__(self):
        try:
            self.conn = sqlite3.connect("rsafactor.db")
            c = self.conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS statistics (method TEXT NOT NULL, bits INT NOT NULL, time BIGINT NOT NULL)")
            self.conn.commit()
            c.close()
        except Error as e:
            print(e)

    def save_statistics(self, results, method):
        c = self.conn.cursor()
        c.executemany("INSERT INTO statistics VALUES (?, ?, ?)", [(method, key if key is not None else -1, item) for key, value in results.items() for item in value])
        self.conn.commit()
        c.close()

    def retrieve_statistics(self):
        c = self.conn.cursor()
        c.execute("SELECT method FROM statistics GROUP BY method")
        method_names = c.fetchall()
        stats = [(self.stat_from_method(method[0], c), method[0]) for method in method_names]
        c.close()
        return stats

    def stat_from_method(self, method, c):
        c.execute("SELECT bits, avg(time) FROM statistics WHERE method=? GROUP BY bits", (method,))
        results = c.fetchall()
        bits = [result[0] for result in results]
        time = [result[1] for result in results]
        return (bits, time)

    def close_connection(self):
        self.conn.close()



