from ..database.db_connector import DbConnector
from ..text_handling.sentence_extractor import SentenceExtractor
from ..text_handling.sentence import JapaneseSentence
from ..text_handling.word import JapaneseWord
from ..anki.anki_connector import AnkiConnector
from ..anki.anki_word_adder import AnkiAdder


class GPTSentenceReplacer:

    sentence_extractor = SentenceExtractor()
    db_connector = DbConnector()
    anki_connector = AnkiConnector()
    anki_adder = AnkiAdder()

    def __init__(self):
        pass

    def replace_sentences_not_genereated_with_gpt(self):
        sentences = self.db_connector.get_sentences_not_generated_by_gpt()
        for sentence in sentences:
            self._generate_new_sentence_and_update_old(sentence)

    def _generate_new_sentence_and_update_old(self, old_sentence: JapaneseSentence):
        new_sentence = self.sentence_extractor.extract_sentence(old_sentence.sentence)
        for new_word in new_sentence.words:
            word_in_db = self.db_connector.get_word_if_exists(
                word_in_kana=new_word.word, reading=new_word.reading
            )
            if word_in_db:
                self._update_word_definition(new_word, word_in_db)
            else:
                self._add_new_word(new_word)
        self.db_connector.update_sentence(new_sentence)
        self.anki_connector.update_sentence(new_sentence)

    def _add_new_word(self, new_word: JapaneseWord):
        if new_word.is_fully_defined():
            added_word = self.db_connector.add_word_if_new(new_word)
            self.anki_adder.add_word_note(added_word)
        else:
            print(
                "WARNING: Tried to add new word in sentence update, but it was not fully defined: ",
                new_word.romaji,
                ", can't be added to db",
            )

    def _update_word_definition(self, new_word: JapaneseWord, word_in_db: JapaneseWord):
        self.db_connector.change_word_definition(
            word_id=word_in_db.db_id, new_definition=new_word.definition
        )
        new_anki_card_back = new_word.romaji + " - " + new_word.definition
        self.anki_connector.update_card_back(word_in_db.anki_id, new_anki_card_back)
