# adds missing romaji to sentence db
from ..database.db_connector import DbConnector
from ..gpt.open_ai_connector import OpenAiConnector
from ..text_handling.sentence import JapaneseSentence


class RomajiAdder:

    db_connector = DbConnector()
    open_ai_connector = OpenAiConnector()

    def __init__(self):
        pass

    def add_missing_sentence_romaji(self):
        print("Adding missing romaji...")
        sentences = self.db_connector.get_sentences_without_romaji()
        for sentence in sentences:
            romaji = self.open_ai_connector.convert_to_romaji(sentence.sentence)
            self.db_connector.update_sentence_romaji(sentence.db_id, romaji)
        print("Finished adding missing romaji")
