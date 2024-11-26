from ..database.db_connector import DbConnector
from ..gpt.open_ai_connector import OpenAiConnector
from ..text_handling.sentence import JapaneseSentence
from ..text_handling.word import JapaneseWord


class CrossrefAdder:

    db_connector = DbConnector()
    open_ai_connector = OpenAiConnector()

    def __init__(self):
        pass

    def add_missing_crossrefs(self):
        print("adding missing crossrefs...")
        sentences = self.db_connector.get_sentences_without_word_crossrefs()
        print("sentences without crossrefs: ", len(sentences))
        for idx, sentence in enumerate(sentences):
            print(idx, " adding crossref to sentece...")
            words = self.open_ai_connector.get_sentence_data(sentence.sentence).words
            for word in words:
                db_id = self.db_connector.get_word_if_exists(
                    word.word, word.reading
                ).db_id
                self.db_connector.add_crossref(db_id, sentence.db_id)
        print("all missing crossrefs added")
