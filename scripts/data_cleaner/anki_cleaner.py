# cleans the data in anki
from ..anki.anki_connector import AnkiConnector
from ..database.vocabulary_connector import VocabularyConnector
from ..text_handling.japanese_word import JapaneseWord
from ..text_handling.sentence import JapaneseSentence
from ..anki.anki_word_adder import add_card_to_anki_deck


class AnkiCleaner:
    def __init__(self):
        pass

    def clean_data(self):
        self._add_missing_cards()
        print("Anki cleaning finished")

    def _add_missing_cards(self):

        connector = AnkiConnector()
        vocab_connector = VocabularyConnector()

        cards = connector.get_all_anki_cards()
        anki_card_definitions: list[str] = [
            card["fields"]["Back"]["value"] for card in cards
        ]

        words_in_db: list[JapaneseWord] = vocab_connector.get_all_words()
        for word in words_in_db:
            word_missing_from_anki = word.definition not in anki_card_definitions
            if word_missing_from_anki:
                add_card_to_anki_deck(word.audio_file_path, word.definition)

        sentences_in_db: list[JapaneseSentence] = vocab_connector.get_all_sentences()
        for sentence in sentences_in_db:
            sentence_missing_from_anki = (
                sentence.definition not in anki_card_definitions
            )
            if sentence_missing_from_anki:
                add_card_to_anki_deck(sentence.audio_file_path, sentence.definition)
