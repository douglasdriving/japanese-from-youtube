import sqlite3
from ..text_handling.japanese_word import JapaneseWord
from ..text_handling.sentence import JapaneseSentence


class VocabularyConnector:
    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()

    def add_word(self, word: JapaneseWord, audio_file_path: str):
        if not word.is_fully_defined():
            print("ERROR: Word is not fully defined. Not adding to database.")
            print(word)
            return
        try:
            self.cursor.execute(
                """
      INSERT INTO vocabulary (word, reading, definition, audio_file_path)
      VALUES (?, ?, ?, ?)
      """,
                (word.word, word.reading, word.definition, audio_file_path),
            )
            self.connection.commit()
        except sqlite3.Error as error:
            print("ERROR INSERTING WORD: ", error)

    def clear_database(self):
        self.cursor.execute(
            """
    DELETE FROM vocabulary
    """
        )
        self.connection.commit()

    def check_if_word_exists(self, word_in_kanji: str):
        self.cursor.execute(
            """
    SELECT * FROM vocabulary WHERE word = (?)
    """,
            (word_in_kanji,),
        )
        word_exists = self.cursor.fetchone() is not None
        return word_exists

    def add_sentence(self, sentence: JapaneseSentence):
        if not sentence.is_fully_defined():
            print("ERROR: Sentence is not fully defined. Not adding to database.")
            print(sentence)
            return
        if self.check_if_sentence_exists(sentence.sentence):
            print(
                "skipping adding sentence to db since it already exists: ",
                sentence.sentence,
            )
            return
        self._insert_sentence_in_db(sentence)

    def _insert_sentence_in_db(self, sentence):
        try:
            self.cursor.execute(
                """
      INSERT INTO sentences (sentence, definition, audio_file_path)
      VALUES (?, ?, ?, ?)
      """,
                (
                    sentence.sentence,
                    sentence.definition,
                    sentence.audio_file,
                ),
            )
            self.connection.commit()
        except sqlite3.Error as error:
            print("ERROR INSERTING SENTENCE: ", error)

    def check_if_sentence_exists(self, sentence):
        self.cursor.execute(
            """
    SELECT * FROM sentences WHERE sentence = (?)
    """,
            (sentence,),
        )
        return self.cursor.fetchone() is not None
