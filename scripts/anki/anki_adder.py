import os
from .anki_note import AnkiNote
from ..text_handling.sentence import JapaneseSentence
from ..text_handling.word import JapaneseWord
from ..text_handling.romaziner import Romanizer
from .anki_connector import AnkiConnector
from .anki_updater import AnkiUpdater
from .anki_getter import AnkiGetter
from ..database.db_connector import DbConnector
from dotenv import load_dotenv


class AnkiAdder:

    deck_name: str
    anki_connect_url: str
    anki_path: str
    anki_connector: AnkiConnector
    anki_getter: AnkiGetter
    anki_updater = AnkiUpdater()
    vocabulary_connector: DbConnector

    def __init__(self):
        load_dotenv()
        self.deck_name = os.environ["ANKI_DECK_NAME"]
        self.anki_connect_url = os.environ["ANKI_CONNECT_URL"]
        self.anki_path = os.environ["ANKI_PATH"]
        self.anki_connector = AnkiConnector()
        self.vocabulary_connector = DbConnector()

    # TODO: create note maker class
    def make_sentence_note(self, sentence: JapaneseSentence):
        romanizer = Romanizer()
        sentence_romaji = romanizer.romanize_with_spaces(sentence.sentence)
        note_back = (
            sentence.definition + "<br><br>" + sentence_romaji + "<br><br>Words:"
        )
        for word in sentence.words:
            if word.reading is not None:
                word_romaji = romanizer.romanize_with_spaces(word.reading)
                note_back += f"<br>{word_romaji} - {word.definition}"
            else:
                print(
                    f"Warning: Word {word.word} has no reading. This will be skipped in the Anki note."
                )
        note = AnkiNote(
            sentence.audio_file_path, note_back, ["sentence"], sentence.db_id
        )
        return note

    def add_words_and_sentences_to_anki(self, sentences: list[JapaneseSentence]):
        self.anki_connector.open_anki_if_not_running()
        notes: list[AnkiNote] = []
        for sentence in sentences:
            for word in sentence.words:
                if word.db_id is None:
                    print(
                        f"Warning: Word {word.word} has no database ID. Skipping adding to Anki."
                    )
                    continue
                notes.append(
                    AnkiNote(
                        word.audio_file_path, word.definition, ["word"], word.db_id
                    )
                )
                # this is gonna contain a lot of duplicates
                # what we could do is: when retrieving words, get their anki ID if there is one
                # if there is an ID here, it means the word is already in anki, so we dont add it
                # hmm... well the problem is probably that when we get the word, we dont get it from anki, we get it from the db
                # and we havent stored the anki ID in the db yet
                # so we kinda need to do that first
                # that is up to the cleaner to do though! grab all anki ids and store them in the DB for crossref
            if sentence.db_id is None:
                print(
                    f"Warning: Sentence {sentence.sentence} has no database ID. Skipping adding to Anki."
                )
                continue
            sentence_note = self.make_sentence_note(sentence)
            notes.append(sentence_note)
        self.add_notes_to_anki_and_mark_in_db(notes)

    def add_sentence_note(self, sentence: JapaneseSentence):
        note = self.make_sentence_note(sentence)
        note_id = self.add_notes_to_anki_and_mark_in_db([note])[0]
        return note_id

    def add_word_note(self, word: JapaneseWord):
        note = AnkiNote(word.audio_file_path, word.definition, ["word"], word.db_id)
        note_id = self.add_notes_to_anki_and_mark_in_db([note])[0]
        return note_id

    def _get_card_options(self):
        options = (
            {
                "allowDuplicate": False,
                "duplicateScope": "deck",
                "duplicateScopeOptions": {
                    "deckName": self.deck_name,
                    "checkChildren": False,
                    "checkAllModels": False,
                },
            },
        )
        return options

    def _create_anki_audio(self, audio_file_path):
        audio_absolute_path = os.path.abspath(audio_file_path)
        audio_base_name = os.path.basename(audio_file_path)
        audio = [
            {
                "path": audio_absolute_path,
                "filename": audio_base_name,
                "skipHash": "7e2c2f954ef6051373ba916f000168dc",
                "fields": ["Front"],
            }
        ]
        return audio

    def _check_which_notes_can_be_added(self, notes: list):
        return self.anki_connector.post_request(
            "canAddNotesWithErrorDetail", {"notes": notes}
        )

    # this is pretty long, might want to refactor
    def _add_notes_to_anki(self, notes_to_add: list[AnkiNote]):
        self.anki_connector.open_anki_if_not_running()

        notes = []
        for note_to_add in notes_to_add:
            note = {
                "deckName": self.deck_name,
                "modelName": "Basic",
                "fields": {"Front": "", "Back": note_to_add.back},
                "tags": note_to_add.tags,
                "options": self._get_card_options(),
                "audio": self._create_anki_audio(note_to_add.audio_file_path),
            }
            notes.append(note)

        which_ones_can_be_added = self._check_which_notes_can_be_added(notes)

        # filter out those that cant, and print why
        valid_notes = []
        for idx, add_check in enumerate(which_ones_can_be_added):
            note = notes[idx]
            if add_check["canAdd"] == False:
                print(
                    "Unable to add note: ",
                    " (",
                    note["fields"]["Front"],
                    "), (",
                    note["fields"]["Back"],
                    ")",
                    " Reason: ",
                    add_check["error"],
                )
            else:
                valid_notes.append(note)

        added_note_ids = self.anki_connector.post_request(
            "addNotes", {"notes": valid_notes}
        )
        if added_note_ids is None:
            print(f"Failed to add card to Anki deck. Error: {response_json['error']}")
        else:
            print(len(added_note_ids), " cards added to Anki deck")
        return added_note_ids

    def _mark_notes_in_db(
        self, notes_to_add: list[AnkiNote], added_note_ids: list[int]
    ):
        added_notes = self.anki_getter.get_notes(added_note_ids)
        for added_note in added_notes:
            for note_to_add in notes_to_add:
                if note_to_add.back == added_note["fields"]["Back"]["value"]:
                    anki_id = added_note["noteId"]
                    table_name = (
                        "vocabulary" if "word" in note_to_add.tags else "sentences"
                    )
                    db_id = note_to_add.db_id
                    self.vocabulary_connector.update_anki_note_id(
                        table_name, db_id, anki_id
                    )
                    break

    def add_notes_to_anki_and_mark_in_db(self, notes_to_add: list[AnkiNote]):
        added_note_ids = self._add_notes_to_anki(notes_to_add)
        if added_note_ids is None:
            print("Anki adder returned to note ids. Skipping marking in DB")
        else:
            self._mark_notes_in_db(notes_to_add, added_note_ids)
            return added_note_ids
