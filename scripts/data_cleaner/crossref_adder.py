from ..database.db_connector import DbConnector
from ..database.word.db_word_getter import DbWordGetter
from ..database.sentence.db_sentence_adder import DbSentenceAdder
from ..database.sentence.db_sentence_deleter import DbSentenceDeleter
from ..database.sentence.db_sentence_getter import DbSentenceGetter
from ..gpt.open_ai_connector import OpenAiConnector


class CrossrefAdder:

    db_connector = DbConnector()
    db_word_getter = DbWordGetter()
    db_sentence_adder = DbSentenceAdder()
    db_sentence_deleter = DbSentenceDeleter()
    db_sentence_getter = DbSentenceGetter()
    open_ai_connector = OpenAiConnector()

    def __init__(self):
        pass

    def add_missing_crossrefs(self):
        sentences = self.db_sentence_getter.get_sentences_without_word_crossrefs()
        if len(sentences) == 0:
            return
        print("adding crossrefs to ", len(sentences), " sentences")
        for idx, sentence in enumerate(sentences):
            print(idx, " adding crossref to sentece: ", sentence.romaji)
            gpt_sentence = self.open_ai_connector.get_sentence_data(sentence.sentence)
            if gpt_sentence is None:
                print(
                    "GPT was unable to get data, so cant add crossrefs. deleting sentence from db: ",
                    sentence.romaji,
                )
                self.db_sentence_deleter.delete_sentence(sentence_id=sentence.db_id)
                continue
            for word in gpt_sentence.words:
                word_in_db = self.db_word_getter.get_word_if_exists(
                    word.word, word.reading
                )
                if word_in_db:
                    self.db_sentence_adder.add_crossref(
                        word_in_db.db_id, sentence.db_id
                    )
                else:
                    print("word not in db: ", word.romaji, " cant make crossref")
        print("all missing crossrefs added")
