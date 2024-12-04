from ..text_handling.sentence_extractor import SentenceExtractor
from ..text_handling.sentence import JapaneseSentence
from ..text_handling.word import JapaneseWord
from ..database.sentence.db_sentence_adder import DbSentenceAdder
from ..database.word.db_word_adder import DbWordAdder
from ..anki.anki_adder import AnkiAdder


class SentenceAdder:

    sentece_extractor = SentenceExtractor()
    db_sentence_adder = DbSentenceAdder()
    db_word_adder = DbWordAdder()
    anki_adder = AnkiAdder()

    def __init__(self):
        pass

    def add_sentence_manually(self):
        user_input = input("Please enter sentence to add (in kana): ")
        while not all(
            "\u3040" <= char <= "\u30ff" or "\u4e00" <= char <= "\u9faf"
            for char in user_input
        ):
            user_input = input(
                "Sentence is not in kana. Please enter sentence to add (in kana): "
            )
        self.add_sentence(user_input)

    def add_sentence(self, sentence_kana: str):
        sentence = self.sentece_extractor.extract_sentence(sentence_kana)
        if sentence.words is not None:
            sentence.words = self._add_new_words_and_attach_ids_to_old_ones(
                sentence.words
            )
        sentence = self.db_sentence_adder.add_sentence_if_new(sentence)
        self.anki_adder.add_sentence_note(sentence)
        return sentence

    def _add_new_words_and_attach_ids_to_old_ones(self, words: list[JapaneseWord]):
        added_words: list[JapaneseWord] = []
        for word in words:
            word = self.db_word_adder.add_word_if_new(word)
            if word:
                if word.anki_id is None:
                    anki_id = self.anki_adder.add_word_note(word)
                    word.anki_id = anki_id
                added_words.append(word)
        return added_words
