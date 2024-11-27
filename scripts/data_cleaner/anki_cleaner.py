# cleans the data in anki
from ..anki.anki_connector import AnkiConnector
from ..database.db_connector import DbConnector
from ..text_handling.word import JapaneseWord
from ..text_handling.sentence import JapaneseSentence
from ..anki.anki_adder import AnkiAdder
from ..anki.anki_note import AnkiNote
from ..anki.anki_getter import AnkiGetter
from ..anki.anki_updater import AnkiUpdater
from ..anki.anki_note_maker import AnkiNoteMaker
from ..anki.anki_deleter import AnkiDeleter
from ..text_handling.sentence_extractor import SentenceExtractor
import re


class AnkiCleaner:

    anki_connector: AnkiConnector
    db_connector: DbConnector
    anki_word_adder: AnkiAdder
    anki_getter = AnkiGetter()
    anki_updater = AnkiUpdater()
    anki_note_maker = AnkiNoteMaker()
    anki_deleter = AnkiDeleter()
    sentence_extractor: SentenceExtractor

    def __init__(self):
        self.anki_connector = AnkiConnector()
        self.db_connector = DbConnector()
        self.anki_word_adder = AnkiAdder()
        self.sentence_extractor = SentenceExtractor(None)

    def clean(self):
        print("Cleaning anki data...")
        self._remove_incorrect_notes()
        self._add_missing_notes()
        self._correct_poor_card_backs()
        self._add_missing_card_tags()
        print("Anki cleaning finished")

    def _remove_incorrect_notes(self):
        print("checking if there are any notes in anki to remove...")
        sentences_in_db = self.db_connector.get_all_sentences()

        # remove locked sentences from anki
        for idx, sentence in enumerate(sentences_in_db):
            if sentence.locked == False:
                continue
            if sentence.anki_id is None:
                continue
            self.anki_deleter.delete_notes([sentence.anki_id])
            self.db_connector.remove_anki_id_from_sentence(sentence.db_id)
            sentences_in_db.pop(idx)
            print("deleted locked sentence from anki: ", sentence.romaji)

        # remove notes in anki that are not in db
        words_in_db = self.db_connector.get_all_words()
        anki_ids_in_db = [sentence.anki_id for sentence in sentences_in_db] + [
            word.anki_id for word in words_in_db
        ]
        print("notes in db: ", len(anki_ids_in_db))
        all_notes = self.anki_getter.get_all_notes()
        print("notes in anki: ", len(all_notes))
        ids_of_notes_to_delete = [
            note["noteId"]
            for note in all_notes
            if (note["noteId"] not in anki_ids_in_db)
        ]
        print("notes to delete: ", len(ids_of_notes_to_delete))
        self.anki_deleter.delete_notes(ids_of_notes_to_delete)

    def _add_missing_notes(self):

        print("checking if there are any missing cards...")
        cards = self.anki_getter.get_all_cards()
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

        words_in_db: list[JapaneseWord] = self.db_connector.get_all_words()
        for word in words_in_db:
            word_definition_is_in_anki = word.definition in anki_card_definitions
            audio_file_name = word.audio_file_path.split("/")[-1]
            audio_is_in_anki = audio_file_name in anki_card_audio_file_names
            is_in_anki = word_definition_is_in_anki or audio_is_in_anki
            if not is_in_anki:
                notes_to_add.append(
                    AnkiNote(
                        audio_file_path=word.audio_file_path,
                        back=word.definition,
                        tags=["word"],
                        db_id=word.db_id,
                    )
                )

        sentences_in_db: list[JapaneseSentence] = self.db_connector.get_all_sentences()
        for sentence in sentences_in_db:
            definition_is_in_anki = sentence.definition in anki_card_definitions
            audio_file_name = sentence.audio_file_path.split("/")[-1]
            audio_is_in_anki = audio_file_name in anki_card_audio_file_names
            is_in_anki = definition_is_in_anki or audio_is_in_anki
            if not is_in_anki:
                note = self.anki_note_maker.make_sentence_note(sentence)
                notes_to_add.append(note)

        print(
            "words + sentences in db: ",
            len(words_in_db) + len(sentences_in_db),
        )

        if len(notes_to_add) > 0:
            print("adding missing notes: ", len(notes_to_add))
            self.anki_word_adder.add_notes_to_anki_and_mark_in_db(notes_to_add)
        else:
            print("No missing cards found")

    def _correct_poor_card_backs(self):
        print("Checking if there are any poorly formatted card backs to update...")
        bad_sentence_notes = self._get_bad_sentence_notes()
        if len(bad_sentence_notes) == 0:
            print("No bad sentence cards found")
            return
        for idx, note in enumerate(bad_sentence_notes):
            print(
                "Updating bad sentence card ",
                idx + 1,
                " of ",
                len(bad_sentence_notes),
                "...",
            )
            self._update_sentence_card_back(note)
        print("All bad sentence cards updated")

    def _get_bad_sentence_notes(self):
        all_notes = self.anki_getter.get_all_notes()
        return [note for note in all_notes if self._is_bad_sentence_note(note)]

    def _is_bad_sentence_note(self, note):
        back = note["fields"]["Back"]["value"]
        is_sentence = self._is_probably_sentence(
            note
        )  # ideally, we should use a note here instead.
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

    def _is_probably_sentence(self, note):

        has_sentence_tag = "sentence" in note["tags"]
        has_word_tag = "word" in note["tags"]
        if has_sentence_tag:
            return True
        if has_word_tag:
            return False

        front = note["fields"]["Front"]["value"]
        back = note["fields"]["Back"]["value"]

        new_front_pattern = re.compile(r"\[sound:[sw]\d+\.wav\]")
        card_uses_new_front_pattern = new_front_pattern.match(front) is not None

        is_sentence = False
        if card_uses_new_front_pattern:
            is_sentence = ":s" in front
        else:
            contains_words = "Words:" in back
            contains_line_breaks = "<br>" in back or "\n" in back
            audio_file_name_contains_underscores = front.count("_") > 1
            is_sentence = (
                contains_words
                or contains_line_breaks
                or audio_file_name_contains_underscores
            )

        return is_sentence

    def _update_sentence_card_back(self, note):
        back = note["fields"]["Back"]["value"]
        english_sentence = re.split(r"<br\s*/?>|\n", back)[0]
        japanese_sentence = (
            self.sentence_extractor.extract_sentence_from_db_by_definition(
                english_sentence
            )  # this wont get the words, since we havent cross-reffed that yet.
            # maybe just retrieve the kana for it
            # and then re-create it using GPT
            # and use the re-created sentence to create new card back
        )
        if japanese_sentence is None:
            print(
                "ERROR: Could not extract data to update card back: ", english_sentence
            )
        else:
            anki_note: AnkiNote = self.anki_note_maker.make_sentence_note(
                japanese_sentence
            )
            new_back = anki_note.back
            note_id = note["noteId"]
            self.anki_updater.update_card_back(note_id, new_back)

    def _add_missing_card_tags(self):

        def _is_tagged(note):
            tags = note["tags"]
            is_tagged_as_word_or_sentence = "word" in tags or "sentence" in tags
            return is_tagged_as_word_or_sentence

        print("Checking if there are any missing card tags...")
        notes = self.anki_getter.get_all_notes()
        id_of_notes_to_tag_as_word = []
        if_of_notes_to_tag_as_sentence = []
        for idx, note in enumerate(notes):
            if not _is_tagged(note):
                is_probably_sentence = self._is_probably_sentence(note)
                note_id = note["noteId"]
                if is_probably_sentence:
                    if_of_notes_to_tag_as_sentence.append(note_id)
                else:
                    id_of_notes_to_tag_as_word.append(note_id)
        if len(id_of_notes_to_tag_as_word) > 0:
            print("Adding word tag to notes: ", len(id_of_notes_to_tag_as_word))
            self.anki_updater.tag_notes(id_of_notes_to_tag_as_word, "word")
        if len(if_of_notes_to_tag_as_sentence) > 0:
            print("Adding sentence tag to notes: ", len(if_of_notes_to_tag_as_sentence))
            self.anki_updater.tag_notes(if_of_notes_to_tag_as_sentence, "sentence")
        if (
            len(id_of_notes_to_tag_as_word) == 0
            and len(if_of_notes_to_tag_as_sentence) == 0
        ):
            print("No missing tags found")
        print("All missing tags added")
