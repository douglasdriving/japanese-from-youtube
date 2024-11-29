from scripts.database.db_connector import DbConnector
from ...text_handling.word import JapaneseWord
import sqlite3


class DbWordGetter:

    connector = DbConnector()

    def __init__(self):
        pass

    def get_all_words(self):
        self.connector.cursor.execute(
            """
            SELECT * FROM vocabulary
            """
        )
        data = self.connector.cursor.fetchall()
        return self._turn_words_data_into_words(data)

    def get_words_without_anki_note_id(self):
        self.connector.cursor.execute(
            """
            SELECT * FROM vocabulary WHERE anki_note_id IS NULL
            """
        )
        data = self.connector.cursor.fetchall()
        return self._turn_words_data_into_words(data)

    def get_words_with_no_crossrefs(self):
        self.connector.cursor.execute(
            """
            SELECT * FROM vocabulary
            WHERE id NOT IN (
                SELECT word_id FROM words_sentences
            )
            """
        )
        data = self.connector.cursor.fetchall()
        return self._turn_words_data_into_words(data)

    def get_words_without_progress(self):
        try:
            self.connector.cursor.execute(
                """
                SELECT * FROM vocabulary WHERE practice_interval = 0
                """
            )
            data = self.connector.cursor.fetchall()
            return self._turn_words_data_into_words(data)
        except sqlite3.Error as error:
            print("ERROR GETTING WORDS WITHOUT PROGRESS: ", error)
            return []

    def get_words_popilarity(self, words: list[JapaneseWord]):
        word_popularity = {}
        for word in words:
            word_popularity[word] = self._get_word_popularity(word)
        return word_popularity

    def _get_word_popularity(self, word: JapaneseWord):
        self.connector.cursor.execute(
            """
            SELECT * FROM words_sentences WHERE word_id = ?
            """,
            (word.db_id,),
        )
        data = self.connector.cursor.fetchall()
        return len(data)

    def get_word_if_exists(self, word_in_kana: str):
        self.connector.cursor.execute(
            """
                SELECT * FROM vocabulary WHERE word = (?)
            """,
            (word_in_kana,),
        )
        word_data = self.connector.cursor.fetchone()
        if word_data is None:
            return None
        else:
            return self._turn_word_data_into_word(word_data)

    def get_words_for_sentence(self, sentence_id: int):
        self.connector.cursor.execute(
            """
            SELECT * FROM vocabulary
            JOIN words_sentences ON vocabulary.id = words_sentences.word_id
            WHERE words_sentences.sentence_id = (?)
            """,
            (sentence_id,),
        )
        data = self.connector.cursor.fetchall()
        return self._turn_words_data_into_words(data)

    def get_word_if_exists(self, word_in_kana: str, reading: str):
        self.connector.cursor.execute(
            """
                SELECT * FROM vocabulary WHERE word = (?) AND reading = (?)
            """,
            (word_in_kana, reading),
        )
        word_data = self.connector.cursor.fetchone()
        if word_data is None:
            return None
        else:
            return self._turn_word_data_into_word(word_data)

    def _turn_words_data_into_words(self, data):
        words: list[JapaneseWord] = []
        for row in data:
            words.append(self._turn_word_data_into_word(row))
        return words

    # TODO: make sure this function is used by all word extractions
    def _turn_word_data_into_word(self, word_row):
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
