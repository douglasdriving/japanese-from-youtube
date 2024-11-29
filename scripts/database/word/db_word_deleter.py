from ..db_connector import DbConnector
import sqlite3


class DbWordDeleter:
    connector = DbConnector()

    def __init__(self):
        pass

    def delete_words(self, ids: list[int]):
        try:
            self.connector.cursor.executemany(
                """
                DELETE FROM vocabulary
                WHERE id = ?
                """,
                [(id,) for id in ids],
            )
            self.connector.connection.commit()
            print(f"Deleted words with ids: {ids}")
        except sqlite3.Error as error:
            print("ERROR DELETING WORDS: ", error)
