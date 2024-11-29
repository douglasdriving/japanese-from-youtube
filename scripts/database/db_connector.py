import sqlite3


class DbConnector:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()

    # TODO: write generic db query methods here, so that we dont have to repeat code in other classes
