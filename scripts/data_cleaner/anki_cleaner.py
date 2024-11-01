# cleans the data in anki
from ..anki.anki_connector import AnkiConnector
from ..database.vocabulary_connector import VocabularyConnector
from ..text_handling.japanese_word import JapaneseWord
from ..text_handling.sentence import JapaneseSentence
from ..anki.anki_word_adder import add_notes_to_anki, make_sentence_note
from ..anki.anki_note import AnkiNote
from ..text_handling.sentence_data_extractor import SentenceDataExtractor
import re


class AnkiCleaner:

    anki_connector: AnkiConnector
    vocab_connector: VocabularyConnector
    sentence_extractor: SentenceDataExtractor

    def __init__(self):
        self.anki_connector = AnkiConnector()
        self.vocab_connector = VocabularyConnector()
        self.sentence_extractor = SentenceDataExtractor()

    def clean_data(self):
        self._add_missing_cards()
        self._correct_poor_card_backs()
        print("Anki cleaning finished")

    def _add_missing_cards(self):

        cards = self.anki_connector.get_all_anki_cards()
        anki_card_definitions: list[str] = [
            card["fields"]["Back"]["value"] for card in cards
        ]

        print("ADDING MISSING CARDS: cards in anki: ", len(anki_card_definitions))
        notes_to_add: list[AnkiNote] = []

        words_in_db: list[JapaneseWord] = self.vocab_connector.get_all_words()
        for word in words_in_db:
            word_missing_from_anki = word.definition not in anki_card_definitions
            if word_missing_from_anki:
                notes_to_add.append(AnkiNote(word.audio_file_path, word.definition))

        sentences_in_db: list[JapaneseSentence] = (
            self.vocab_connector.get_all_sentences()
        )
        for sentence in sentences_in_db:
            sentence_missing_from_anki = (
                sentence.definition not in anki_card_definitions
            )
            if sentence_missing_from_anki:
                notes_to_add.append(
                    AnkiNote(sentence.audio_file_path, sentence.definition)
                )

        print(
            "ADDING MISSING CARDS: number of words and sentences in db: ",
            len(words_in_db) + len(sentences_in_db),
        )

        if len(notes_to_add) > 0:
            print("ADDING MISSING CARDS: number of notes to add: ", len(notes_to_add))
            add_notes_to_anki(notes_to_add)

    def _correct_poor_card_backs(self):
        cards = self.anki_connector.get_all_anki_cards()
        for card in cards:
            self._correct_card_if_bad(card)

    def _correct_card_if_bad(self, card):

        def _sentence_back_has_right_format(back: str):
            has_two_double_line_breaks = back.count("<br><br>") == 2
            contains_words = "Words:" in back
            has_right_format = has_two_double_line_breaks and contains_words
            return has_right_format

        back = card["fields"]["Back"]["value"]
        is_sentence = self._is_sentence_card(card)
        if is_sentence:
            has_right_format = _sentence_back_has_right_format(back)
            if not has_right_format:
                self._update_sentence_card_back(card)

    def _is_sentence_card(self, card):

        front = card["fields"]["Front"]["value"]
        back = card["fields"]["Back"]["value"]

        new_front_pattern = re.compile(r"\[sound:[sw]\d+\.wav\]")
        card_uses_new_front_pattern = new_front_pattern.match(front) is not None

        is_sentence = False
        if card_uses_new_front_pattern:
            is_sentence = ":s" in front
        else:
            is_sentence = "_" in front

        return is_sentence

    def _update_sentence_card_back(self, card):
        back = card["fields"]["Back"]["value"]
        english_sentence = back.split("<br><br>")[0]
        japanese_sentence = self.sentence_extractor.extract_db_data_for_sentence(
            english_sentence
        )
        if japanese_sentence is None:
            print(
                "ERROR: Could not extract data to update card back: ", english_sentence
            )
        else:
            note: AnkiNote = make_sentence_note(japanese_sentence)
            self.anki_connector.update_card_back(card["cardId"], note.back)
            print("Updated card back: ", english_sentence)
