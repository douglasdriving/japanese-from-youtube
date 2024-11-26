from ..database.db_connector import DbConnector
from ..gpt.open_ai_connector import OpenAiConnector


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
            print(idx, " adding crossref to sentece: ", sentence.romaji)
            words = self.open_ai_connector.get_sentence_data(sentence.sentence).words
            for word in words:
                word_in_db = self.db_connector.get_word_if_exists(
                    word.word, word.reading
                )
                if word_in_db:
                    self.db_connector.add_crossref(word_in_db.db_id, sentence.db_id)
                else:
                    print("word not in db: ", word.romaji, " cant make crossref")
        print("all missing crossrefs added")
