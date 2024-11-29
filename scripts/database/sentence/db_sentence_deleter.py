from ..db_connector import DbConnector
import sqlite3


class DbSentenceDeleter:
    connector = DbConnector()

    def __init__(self):
        pass

    def delete_sentence(self, sentence_id: int):
        try:
            self.connector.cursor.execute(
                """
                DELETE FROM sentences
                WHERE id = ?
                """,
                (sentence_id,),
            )
            self.connector.connection.commit()
            print(f"Deleted sentence with id {sentence_id}")
        except sqlite3.Error as error:
            print("ERROR DELETING SENTENCE: ", error)

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
