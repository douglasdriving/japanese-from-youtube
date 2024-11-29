from ..db_connector import DbConnector
from .db_word_updater import DbWordUpdater
from .db_word_getter import DbWordGetter
from ...text_handling.word import JapaneseWord
import sqlite3


class DbWordAdder:

    connector = DbConnector()
    updater = DbWordUpdater()
    getter = DbWordGetter()

    def __init__(self):
        pass

    def add_word_if_new(self, word: JapaneseWord):

        if not word.is_fully_defined():
            print(
                "ERROR: Word is not fully defined. Not adding to database. word: ",
                word.word,
                ", reading: ",
                word.reading,
                ", definition: ",
                word.definition,
                ", audio_file_path: ",
                word.audio_file_path,
            )
            return word

        word_in_db = self.getter.get_word_if_exists(word.word, word.reading)
        if word_in_db is not None:
            updated_definition = self.updater.add_definition_to_word_if_new(
                word_id=word.db_id, new_definition=word.definition
            )
            word_in_db.definition = updated_definition
            return word_in_db

        try:
            self.connector.cursor.execute(
                """
                    INSERT INTO vocabulary (word, reading, definition, audio_file_path, romaji)
                    VALUES (?, ?, ?, ?, ?)
                """,
                (
                    word.word,
                    word.reading,
                    word.definition,
                    word.audio_file_path,
                    word.romaji,
                ),
            )
            self.connector.connection.commit()
            print(f"Added word '{word.romaji}' ({word.definition}) to database")
            id = self.connector.cursor.lastrowid
            word.db_id = id
            return word
        except sqlite3.Error as error:
            print("ERROR INSERTING WORD: ", error)
            return None
