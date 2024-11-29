# adds missing romaji to sentence db
from ..database.db_connector import DbConnector
from ..database.sentence.db_sentence_updater import DbSentenceUpdater
from ..gpt.open_ai_connector import OpenAiConnector
from ..database.sentence.db_sentence_getter import DbSentenceGetter


class RomajiAdder:

    db_connector = DbConnector()
    sentence_db_updater = DbSentenceUpdater()
    db_sentence_getter = DbSentenceGetter()
    open_ai_connector = OpenAiConnector()

    def __init__(self):
        pass

    def add_missing_sentence_romaji(self):
        sentences = self.db_sentence_getter.get_sentences_without_romaji()
        if len(sentences) == 0:
            return
        print("Adding missing romaji to", len(sentences), "sentences")
        for sentence in sentences:
            romaji = self.open_ai_connector.convert_to_romaji(sentence.sentence)
            self.sentence_db_updater.update_sentence_romaji(sentence.db_id, romaji)
        print("Finished adding missing romaji")
