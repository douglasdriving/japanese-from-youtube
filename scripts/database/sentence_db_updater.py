from .db_connector import DbConnector
import sqlite3
from ..text_handling.sentence import JapaneseSentence


class SentenceDbUpdater:
    connector = DbConnector()

    def __init__(self):
        pass

    def update_sentence_romaji(self, sentence_id: int, romaji: str):
        try:
            self.connector.cursor.execute(
                """
                UPDATE sentences
                SET romaji = ?
                WHERE id = ?
                """,
                (romaji, sentence_id),
            )
            self.connector.connection.commit()
            print(f"Updated romaji for sentence with id {sentence_id} to '{romaji}'")
        except sqlite3.Error as error:
            print("ERROR UPDATING SENTENCE ROMAJI: ", error)

    def update_sentence(self, sentence: JapaneseSentence):
        try:
            self.connector.cursor.execute(
                """
                    UPDATE sentences
                    SET sentence = ?, definition = ?, audio_file_path = ?, gpt_generated = ?, romaji = ?
                    WHERE id = ?
                    """,
                (
                    sentence.sentence,
                    sentence.definition,
                    sentence.audio_file_path,
                    sentence.gpt_generated,
                    sentence.db_id,
                    sentence.romaji,
                ),
            )
            self.connector.connection.commit()
            print(
                f"Updated sentence with id {sentence.db_id} to '{sentence.sentence}', '{sentence.definition}', '{sentence.audio_file_path}', '{sentence.gpt_generated}'"
            )
        except sqlite3.Error as error:
            print("ERROR UPDATING SENTENCE: ", error)

    def update_sentence_practice_intervals(self, sentences: list[JapaneseSentence]):
        for sentence in sentences:
            self.connector.cursor.execute(
                """
                UPDATE sentences
                SET practice_interval = ?
                WHERE id = ?
                """,
                (sentence.practice_interval, sentence.db_id),
            )
            self.connector.connection.commit()
            print(
                f"Updated practice interval for sentence {sentence.sentence} to {sentence.practice_interval}"
            )
