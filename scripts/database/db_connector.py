import sqlite3
from ..text_handling.word import JapaneseWord
from ..text_handling.sentence import JapaneseSentence
from ..text_handling.romaziner import Romanizer

# TODO: refactor this, break into more classes


class DbConnector:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor
    romanizer = Romanizer()

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()

    # TODO: remove word getter functions
    def get_words_for_sentence(self, sentence_id: int):
        self.cursor.execute(
            """
            SELECT * FROM vocabulary
            JOIN words_sentences ON vocabulary.id = words_sentences.word_id
            WHERE words_sentences.sentence_id = (?)
            """,
            (sentence_id,),
        )
        data = self.cursor.fetchall()
        words: list[JapaneseWord] = []
        for row in data:
            word = self.turn_word_data_into_word(row)
            words.append(word)
        return words

    def turn_word_data_into_word(self, word_row):
        return JapaneseWord(
            database_id=word_row[0],
            word=word_row[1],
            reading=word_row[2],
            definition=word_row[3],
            audio_file_path=word_row[4],
            anki_id=word_row[5],
            romaji=word_row[6],
            practice_interval=word_row[7],
        )
