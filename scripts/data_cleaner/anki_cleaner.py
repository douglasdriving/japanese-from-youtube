# cleans the data in anki
from ..anki.anki_connector import AnkiConnector
from ..database.word_db_connector import WordDbConnector
from ..database.sentence_db_connector import SentenceDbConnector
from ..text_handling.japanese_word import JapaneseWord
from ..text_handling.japanese_sentence import JapaneseSentence
from ..anki.anki_note_adder import AnkiNoteAdder
from ..anki.anki_note import AnkiNote
from ..text_handling.sentence_extractor import SentenceExtractor
import re


class AnkiCleaner:

    anki_connector: AnkiConnector
    vocab_connector: WordDbConnector
    sentence_db_connector: SentenceDbConnector
    anki_word_adder: AnkiNoteAdder
    sentence_extractor: SentenceExtractor

    def __init__(self):
        self.anki_connector = AnkiConnector()
        self.vocab_connector = WordDbConnector()
        self.anki_word_adder = AnkiNoteAdder()
        self.sentence_extractor = SentenceExtractor(None)
        self.sentence_db_connector = SentenceDbConnector()

    def clean(self):
        print("Cleaning anki data...")
        self._add_missing_notes()
        self._delete_notes_not_in_db()
        self._correct_poor_card_backs()
        self._add_missing_card_tags()
        print("Anki cleaning finished")

    def _delete_notes_not_in_db(self):
        sentences_in_db = self.sentence_db_connector.get_all_sentences()
        words_in_db = self.vocab_connector.get_all_words()
        anki_ids_in_db = [sentence.anki_id for sentence in sentences_in_db] + [
            word.anki_id for word in words_in_db
        ]
        all_notes = self.anki_connector.get_all_notes()
        ids_of_notes_to_delete = [
            note["noteId"] for note in all_notes if note["noteId"] not in anki_ids_in_db
        ]
        if len(ids_of_notes_to_delete) > 0:
            self.anki_connector.delete_notes(ids_of_notes_to_delete)
        else:
            print("No notes to delete from anki")

    def _add_missing_notes(self):

        print("checking if there are any missing cards...")
        all_anki_ids = self.anki_connector.get_all_note_ids()
        print("notes in anki: ", len(all_anki_ids))

        words_in_db: list[JapaneseWord] = self.vocab_connector.get_all_words()
        sentences_in_db: list[JapaneseSentence] = (
            self.sentence_db_connector.get_all_sentences()
        )

        notes_to_add: list[AnkiNote] = []

        for word in words_in_db:
            if word.anki_id is None or word.anki_id not in all_anki_ids:
                notes_to_add.append(
                    AnkiNote(word.audio_file_path, word.definition, "word", word.db_id)
                )
        for sentence in sentences_in_db:
            if sentence.anki_id is None or sentence.anki_id not in all_anki_ids:
                notes_to_add.append(
                    AnkiNote(
                        sentence.audio_file_path,
                        sentence.definition,
                        "sentence",
                        sentence.db_id,
                    )
                )

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
        all_notes = self.anki_connector.get_all_notes()
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
        note_id = note["noteId"]
        sentence = self.sentence_db_connector.get_sentence_by_anki_id(
            anki_note_id=note_id
        )
        if sentence is None:
            print("No db data found for anki note with id: ", note_id, " deleting note")
            self.anki_connector.delete_notes([note_id])
        else:
            anki_note: AnkiNote = self.anki_word_adder.make_sentence_note(sentence)
            new_back = anki_note.back
            self.anki_connector.update_card_back(note_id, new_back)

    def _add_missing_card_tags(self):

        def _is_tagged(note):
            tags = note["tags"]
            is_tagged_as_word_or_sentence = "word" in tags or "sentence" in tags
            return is_tagged_as_word_or_sentence

        print("Checking if there are any missing card tags...")
        notes = self.anki_connector.get_all_notes()
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
            self.anki_connector.tag_notes(id_of_notes_to_tag_as_word, "word")
        if len(if_of_notes_to_tag_as_sentence) > 0:
            print("Adding sentence tag to notes: ", len(if_of_notes_to_tag_as_sentence))
            self.anki_connector.tag_notes(if_of_notes_to_tag_as_sentence, "sentence")
        if (
            len(id_of_notes_to_tag_as_word) == 0
            and len(if_of_notes_to_tag_as_sentence) == 0
        ):
            print("No missing tags found")
        print("All missing tags added")
