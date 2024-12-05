# adds missing romaji to sentence db
from ..database.db_connector import DbConnector
from ..database.sentence.db_sentence_updater import DbSentenceUpdater
from ..gpt.open_ai_connector import OpenAiConnector
from ..database.sentence.db_sentence_getter import DbSentenceGetter
from ..database.word.db_word_getter import DbWordGetter
from ..database.word.db_word_updater import DbWordUpdater


class RomajiAdder:

    db_connector = DbConnector()
    sentence_db_updater = DbSentenceUpdater()
    db_sentence_getter = DbSentenceGetter()
    db_word_getter = DbWordGetter()
    db_word_updater = DbWordUpdater()
    open_ai_connector = OpenAiConnector()

    def __init__(self):
        pass

    def add_missing_romaji(self):
        self.add_missing_sentence_romaji()
        self.add_missing_word_romaji()

    def add_missing_sentence_romaji(self):
        sentences = self.db_sentence_getter.get_sentences_without_romaji()
        if len(sentences) == 0:
            return
        print("Adding missing romaji to", len(sentences), "sentences")
        for sentence in sentences:
            romaji = self.open_ai_connector.get_romaji(sentence.sentence)
            self.sentence_db_updater.update_sentence_romaji(sentence.db_id, romaji)
        print("Finished adding missing romaji")

    def add_missing_word_romaji(self):
        words = self.db_word_getter.get_words_without_romaji()
        if len(words) == 0:
            return
        print("Adding missing romaji to", len(words), "words")
        for word in words:
            romaji = self.open_ai_connector.get_romaji(word.word)
            self.db_word_updater.update_word_romaji(word.db_id, romaji)
