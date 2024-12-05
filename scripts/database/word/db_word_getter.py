from scripts.database.db_connector import DbConnector
from ...text_handling.word import JapaneseWord


class DbWordGetter:

    connector = DbConnector()

    def __init__(self):
        pass

    def get_all_words(self):
        return self._get_words()

    def get_words_without_anki_note_id(self):
        return self._get_words("WHERE anki_note_id IS NULL")

    def get_words_with_no_crossrefs(self):
        return self._get_words("WHERE id NOT IN (SELECT word_id FROM words_sentences)")

    def get_words_without_progress(self):
        return self._get_words("WHERE practice_interval IS NULL")

    def get_words_without_romaji(self):
        return self._get_words("WHERE romaji IS NULL")

    def _get_words(self, condition: str = "", values: tuple = ()):
        query = "SELECT * FROM vocabulary"
        if condition != "":
            query += " " + condition
        data = self.connector.fetch_all(query, values)
        words = self._turn_words_data_into_words(data)
        return words

    def get_words_popilarity(self, words: list[JapaneseWord]):
        word_popularity = {}
        for word in words:
            word_popularity[word] = self._get_word_popularity(word)
        return word_popularity

    def _get_word_popularity(self, word: JapaneseWord):
        data = self.connector.fetch_all(
            "SELECT * FROM words_sentences WHERE word_id = ?", (word.db_id,)
        )
        return len(data)

    def get_word_if_exists(self, word_in_kana: str):
        return self._get_word("WHERE word = ?", (word_in_kana,))

    def _get_word(self, condition: str = "", values: tuple = ()):
        query = "SELECT * FROM vocabulary"
        if condition != "":
            query += " " + condition
        data = self.connector.fetch_one(
            query,
            values,
        )
        return self._turn_word_data_into_word(data)

    def get_words_for_sentence(self, sentence_id: int):
        return self._get_words(
            """
            JOIN words_sentences ON vocabulary.id = words_sentences.word_id
            WHERE words_sentences.sentence_id = (?)
            """,
            (sentence_id,),
        )

    def get_word_if_exists(self, word_in_kana: str, reading: str):
        return self._get_word("WHERE word = ? AND reading = ?", (word_in_kana, reading))

    def _turn_words_data_into_words(self, data):
        if data is None or len(data) == 0:
            return []
        words: list[JapaneseWord] = []
        for row in data:
            words.append(self._turn_word_data_into_word(row))
        return words

    def _turn_word_data_into_word(self, word_row):
        if word_row is None:
            return None
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
