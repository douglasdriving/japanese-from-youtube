import os
from .anki_note import AnkiNote
from ..text_handling.sentence import JapaneseSentence
from ..text_handling.word import JapaneseWord
from .anki_connector import AnkiConnector
from .anki_updater import AnkiUpdater
from .anki_getter import AnkiGetter
from .anki_note_maker import AnkiNoteMaker
from ..database.db_connector import DbConnector


class AnkiAdder:

    base_deck_name: str
    word_deck_name: str
    sentence_deck_name: str
    anki_connect_url: str
    anki_path: str
    connector: AnkiConnector
    getter = AnkiGetter()
    updater = AnkiUpdater()
    note_maker = AnkiNoteMaker()
    vocabulary_connector: DbConnector

    def __init__(self):
        self.base_deck_name = os.environ["ANKI_DECK_NAME"]
        self.word_deck_name = os.environ["ANKI_WORD_DECK_NAME"]
        self.sentence_deck_name = os.environ["ANKI_SENTENCE_DECK_NAME"]
        self.anki_connect_url = os.environ["ANKI_CONNECT_URL"]
        self.anki_path = os.environ["ANKI_PATH"]
        self.connector = AnkiConnector()
        self.vocabulary_connector = DbConnector()

    def add_words_and_sentences_to_anki(self, sentences: list[JapaneseSentence]):
        self.connector.open_anki_if_not_running()
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
            sentence_note = self.note_maker.make_sentence_note(sentence)
            notes.append(sentence_note)
        self.add_notes_to_anki_and_mark_in_db(notes)

    def add_sentence_note(self, sentence: JapaneseSentence):
        note = self.note_maker.make_sentence_note(sentence)
        note_id = self.add_notes_to_anki_and_mark_in_db([note])[0]
        return note_id

    def add_word_note(self, word: JapaneseWord):
        note = AnkiNote(word.audio_file_path, word.definition, ["word"], word.db_id)
        added_notes = self.add_notes_to_anki_and_mark_in_db([note])
        if added_notes and len(added_notes) > 0:
            return added_notes[0]
        else:
            return None

    def _get_card_options(self):
        options = (
            {
                "allowDuplicate": False,
                "duplicateScope": "deck",
                "duplicateScopeOptions": {
                    "deckName": self.base_deck_name,
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
        return self.connector.post_request(
            "canAddNotesWithErrorDetail", {"notes": notes}
        )

    # this is pretty long, might want to refactor
    def _add_note_to_anki(self, notes_to_add: list[AnkiNote]):
        self.connector.open_anki_if_not_running()

        notes = []
        for note_to_add in notes_to_add:
            note = {
                "deckName": self.base_deck_name,
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

        response = self.connector.post_request("addNotes", {"notes": valid_notes})
        if response["error"]:
            print(f"Failed to add note to Anki deck. Error: {response['error']}")
        else:
            print(len(response), " cards added to Anki deck")
        return response

    def _mark_note_in_db(self, db_id: int, anki_note_id: int, is_word: bool):
        table_name = "vocabulary" if is_word else "sentences"
        self.vocabulary_connector.update_anki_note_id(table_name, db_id, anki_note_id)

    def add_notes_to_anki_and_mark_in_db(self, notes_to_add: list[AnkiNote]):
        for note in notes_to_add:
            if note.db_id is None:
                print(
                    f"Warning: Note {note.back} has no database ID. Skipping adding to Anki."
                )
                continue
            anki_note_id = self._add_note_to_anki(note)
            if anki_note_id:
                is_word = note.tags and "word" in note.tags
                self._mark_note_in_db(note.db_id, anki_note_id, is_word)
            else:
                print(
                    "Failed to add note to Anki: ", note.back, ", will not mark in DB"
                )

    def _add_note_to_anki(self, note_to_add: AnkiNote):
        self.connector.open_anki_if_not_running()
        deck = self.word_deck_name
        if "sentence" in note_to_add.tags:
            deck = self.sentence_deck_name
        note = {
            "deckName": deck,
            "modelName": "Basic",
            "fields": {"Front": "", "Back": note_to_add.back},
            "tags": note_to_add.tags,
            "options": self._get_card_options(),
            "audio": self._create_anki_audio(note_to_add.audio_file_path),
        }
        anki_id = self.connector.post_request("addNote", {"note": note})
        if anki_id is None:
            print(f"Failed to add note to Anki deck: {note}")
        else:
            print("Anki note added with id: ", anki_id)
        return anki_id