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

        print("checking if there are any missing cards...")
        cards = self.anki_connector.get_all_anki_cards()
        anki_card_definitions: list[str] = [
            re.split(r"<br\s*/?>|\n", card["fields"]["Back"]["value"])[0]
            for card in cards
        ]
        anki_card_audio_file_names: list[str] = [
            re.search(r"\[sound:(.*?)\]", card["fields"]["Front"]["value"]).group(1)
            for card in cards
        ]

        print("cards in anki: ", len(anki_card_definitions))
        notes_to_add: list[AnkiNote] = []

        words_in_db: list[JapaneseWord] = self.vocab_connector.get_all_words()
        for word in words_in_db:
            word_definition_is_in_anki = word.definition in anki_card_definitions
            audio_file_name = word.audio_file_path.split("/")[-1]
            audio_is_in_anki = audio_file_name in anki_card_audio_file_names
            is_in_anki = word_definition_is_in_anki or audio_is_in_anki
            if not is_in_anki:
                notes_to_add.append(AnkiNote(word.audio_file_path, word.definition))

        sentences_in_db: list[JapaneseSentence] = (
            self.vocab_connector.get_all_sentences()
        )
        for sentence in sentences_in_db:
            definition_is_in_anki = sentence.definition in anki_card_definitions
            audio_file_name = sentence.audio_file_path.split("/")[-1]
            audio_is_in_anki = audio_file_name in anki_card_audio_file_names
            is_in_anki = definition_is_in_anki or audio_is_in_anki
            if not is_in_anki:
                notes_to_add.append(
                    AnkiNote(sentence.audio_file_path, sentence.definition)
                )

        print(
            "words + sentences in db: ",
            len(words_in_db) + len(sentences_in_db),
        )

        if len(notes_to_add) > 0:
            print("adding missing notes: ", len(notes_to_add))
            add_notes_to_anki(notes_to_add)
        else:
            print("No missing cards found")

    def _correct_poor_card_backs(self):
        print("Checking if there are any poorly formatted card backs to update...")
        cards = self.anki_connector.get_all_anki_cards()
        bad_sentence_cards = self._get_bad_sentence_cards(cards)
        for idx, card in enumerate(bad_sentence_cards):
            print(
                "Updating bad sentence card ", idx + 1, " of ", len(bad_sentence_cards)
            )
            self._update_sentence_card_back(card)

    def _get_bad_sentence_cards(self, cards):
        return [card for card in cards if self._is_bad_sentence_card(card)]

    def _is_bad_sentence_card(self, card):
        back = card["fields"]["Back"]["value"]
        is_sentence = self._is_sentence_card(card)
        is_bad = False
        if is_sentence:
            has_right_format = self._sentence_back_has_right_format(back)
            if not has_right_format:
                is_bad = True
        return is_bad

    def _sentence_back_has_right_format(self, back: str):
        has_two_double_line_breaks = back.count("<br><br>") == 2
        contains_words = "Words:" in back
        has_right_format = has_two_double_line_breaks and contains_words
        return has_right_format

    def _is_sentence_card(self, card):

        front = card["fields"]["Front"]["value"]
        back = card["fields"]["Back"]["value"]

        new_front_pattern = re.compile(r"\[sound:[sw]\d+\.wav\]")
        card_uses_new_front_pattern = new_front_pattern.match(front) is not None

        is_sentence = False
        if card_uses_new_front_pattern:
            is_sentence = ":s" in front
        else:
            is_sentence = False
            # for now, we are just ignoring the cards with the old structure. its too hard to determine what they are.

        return is_sentence

    def _update_sentence_card_back(self, card):
        back = card["fields"]["Back"]["value"]
        english_sentence = re.split(r"<br\s*/?>|\n", back)[0]
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
