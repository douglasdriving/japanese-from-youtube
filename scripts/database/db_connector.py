import sqlite3

# TODO: write generic db query methods here, so that we dont have to repeat code in other classes


class DbConnector:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()

    def fetch_all(self, query: str, values: tuple = ()):
        try:
            self.cursor.execute(query, values)
            data = self.cursor.fetchall()
            return data
        except sqlite3.Error as error:
            print("ERROR FETCHING ALL DATA: ", error)
            print("QUERY TRIED: ", query)
            return []

    def fetch_one(self, query: str, values: tuple = ()):
        try:
            self.cursor.execute(query, values)
            data = self.cursor.fetchone()
            return data
        except sqlite3.Error as error:
            print("ERROR FETCHING ONE DATA: ", error)
            print("QUERY TRIED: ", query)
            return None
