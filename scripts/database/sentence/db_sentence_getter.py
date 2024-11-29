from ..db_connector import DbConnector
from ..word.db_word_getter import DbWordGetter
from ...text_handling.sentence import JapaneseSentence


class DbSentenceGetter:
    connector = DbConnector()
    word_getter = DbWordGetter()

    def __init__(self):
        pass

    def check_if_sentence_exists(self, kana_sentence: str):
        self.connector.cursor.execute(
            """
            SELECT * FROM sentences WHERE sentence = (?)
            """,
            (kana_sentence,),
        )
        return self.connector.cursor.fetchone() is not None

    def get_all_sentences(self):
        self.connector.cursor.execute(
            """
            SELECT * FROM sentences
            """
        )
        data = self.connector.cursor.fetchall()
        return self._turn_sentences_data_into_objects(data)

    def _turn_sentences_data_into_objects(self, data):
        sentences: list[JapaneseSentence] = []
        for row in data:
            sentences.append(self._turn_sentence_data_into_sentence(row))
        return sentences

    def get_sentences_not_generated_by_gpt(self):
        self.connector.cursor.execute(
            """
            SELECT * FROM sentences WHERE gpt_generated = 0
            """
        )
        data = self.connector.cursor.fetchall()
        return self._turn_sentences_data_into_objects(data)

    def get_sentence_by_definition(self, english_sentence: str):
        self.connector.cursor.execute(
            """
                SELECT * FROM sentences WHERE definition = (?)
            """,
            (english_sentence,),
        )
        sentence_data = self.connector.cursor.fetchone()
        if sentence_data is None:
            return None
        else:
            return self._turn_sentence_data_into_sentence(sentence_data)

    def get_sentence_by_kana_text(self, kana_sentence: str):
        self.connector.cursor.execute(
            """
                SELECT * FROM sentences WHERE sentence = (?)
            """,
            (kana_sentence,),
        )
        sentence_data = self.connector.cursor.fetchone()
        if sentence_data is None:
            return None
        else:
            return self._turn_sentence_data_into_sentence(sentence_data)

    def get_sentences_without_romaji(self):
        self.connector.cursor.execute(
            """
            SELECT * FROM sentences WHERE romaji IS NULL
            """
        )
        data = self.connector.cursor.fetchall()
        return self._turn_sentences_data_into_objects(data)

    def get_sentences_without_word_crossrefs(self):
        self.connector.cursor.execute(
            """
            SELECT * FROM sentences
            WHERE id NOT IN (
                SELECT sentence_id FROM words_sentences
            )
            """
        )
        data = self.connector.cursor.fetchall()
        return self._turn_sentences_data_into_objects(data)

    def get_locked_sentences(self):
        self.connector.cursor.execute(
            """
            SELECT * FROM sentences WHERE locked IS 1
            """
        )
        data = self.connector.cursor.fetchall()
        return self._turn_sentences_data_into_objects(data)

    def _turn_sentence_data_into_sentence(self, sentence_data):
        sentence = JapaneseSentence(
            database_id=sentence_data[0],
            sentence=sentence_data[1],
            definition=sentence_data[2],
            audio_file=sentence_data[3],
            anki_id=sentence_data[4],
            practice_interval=sentence_data[5],
            gpt_generated=sentence_data[6],
            romaji=sentence_data[7],
            words=self.word_getter.get_words_for_sentence(sentence_data[0]),
            locked=(sentence_data[8] == 1),
        )
        # TODO: when this is iterated over every sentence in th db, that leads to a lot of requests. instead, get all words from db and match them to the sentence
        return sentence

    def get_unlocked_sentences_without_anki_note_id(self):
        self.connector.cursor.execute(
            """
            SELECT * FROM sentences WHERE anki_note_id IS NULL AND locked = 0
            """
        )
        data = self.connector.cursor.fetchall()
        return self._turn_sentences_data_into_objects(data)
