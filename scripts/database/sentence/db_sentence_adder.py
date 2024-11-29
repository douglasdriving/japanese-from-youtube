from ..db_connector import DbConnector
from .db_sentence_getter import DbSentenceGetter
from ...text_handling.sentence import JapaneseSentence
import sqlite3


class DbSentenceAdder:
    connector = DbConnector()
    getter = DbSentenceGetter()

    def __init__(self):
        pass

    def add_sentence_if_new(self, sentence: JapaneseSentence):
        if not sentence.is_fully_defined():
            print(
                "ERROR: Sentence is not fully defined. Not adding to database: ",
                sentence.sentence,
                sentence.definition,
                sentence.audio_file_path,
                sentence.words,
                sentence.romaji,
            )
            return None
        if self.getter.check_if_sentence_exists(sentence.sentence):
            return None
        added_sentence = self._insert_sentence_in_db(sentence)
        return added_sentence

    def _insert_sentence_in_db(self, sentence: JapaneseSentence):
        try:
            self.connector.cursor.execute(
                """
            INSERT INTO sentences (sentence, definition, audio_file_path, gpt_generated, romaji)
            VALUES (?, ?, ?, ?, ?)
            """,
                (
                    sentence.sentence,
                    sentence.definition,
                    sentence.audio_file_path,
                    sentence.gpt_generated,
                    sentence.romaji,
                ),
            )
            self.connector.connection.commit()
            print(
                f"Added sentence '{sentence.romaji}' ({sentence.definition}) to database"
            )
            id = self.connector.cursor.lastrowid
            sentence.db_id = id
            for word in sentence.words:
                self._insert_word_sentence_relation(word.db_id, sentence.db_id)
            return sentence
        except sqlite3.Error as error:
            print("ERROR INSERTING SENTENCE: ", error)
            return None

    def _insert_word_sentence_relation(self, word_id: int, sentence_id: int):
        try:
            self.connector.cursor.execute(
                """
                INSERT INTO words_sentences (word_id, sentence_id)
                VALUES (?, ?)
                """,
                (word_id, sentence_id),
            )
            self.connector.connection.commit()
            print(
                f"Added word-sentence relation to database with word_id {word_id} and sentence_id {sentence_id}"
            )
        except sqlite3.Error as error:
            print("ERROR INSERTING WORD SENTENCE RELATION: ", error)

    def add_crossref(self, word_id: int, sentence_id: int):
        try:
            self.connector.cursor.execute(
                """
            INSERT INTO words_sentences (word_id, sentence_id)
            VALUES (?, ?)
            """,
                (word_id, sentence_id),
            )
            self.connector.connection.commit()
            print(
                f"Added crossref between word with id {word_id} and sentence with id {sentence_id}"
            )
        except sqlite3.Error as error:
            print("ERROR ADDING CROSSREF: ", error)
