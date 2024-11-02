import requests
import os
import subprocess
import time
from .anki_note import AnkiNote
from ..text_handling.sentence import JapaneseSentence
from ..text_handling.romaziner import romanize_with_spaces
from .anki_connector import AnkiConnector
from ..database.vocabulary_connector import VocabularyConnector

# this really needs to be a class...

# could move this into env vars
deck_name = "jp_audio_cards"
anki_connect_url = "http://localhost:8765"
anki_path = r"C:\Users\dougl\AppData\Local\Programs\Anki\anki.exe"
anki_connector: AnkiConnector = AnkiConnector()
vocabulary_connector: VocabularyConnector = VocabularyConnector()


def _get_card_options(deck_name):
    options = (
        {
            "allowDuplicate": False,
            "duplicateScope": "deck",
            "duplicateScopeOptions": {
                "deckName": deck_name,
                "checkChildren": False,
                "checkAllModels": False,
            },
        },
    )
    return options


def _create_anki_audio(audio_file_path):
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


def _check_which_notes_can_be_added(notes: list):
    request_json = {
        "action": "canAddNotesWithErrorDetail",
        "version": 6,
        "params": {
            "notes": notes,
        },
    }
    response = requests.post(anki_connect_url, json=request_json)
    response_json = response.json()
    if response_json["result"] is None:
        print(
            f"Failed to check which notes can be added. Error: {response_json['error']}"
        )
    return response_json["result"]


def _add_notes_to_anki(notes_to_add: list[AnkiNote]):
    anki_connector._open_anki_if_not_running()

    notes = []
    for note_to_add in notes_to_add:
        note = {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {"Front": "", "Back": note_to_add.back},
            "tags": note_to_add.tags,
            "options": _get_card_options(deck_name),
            "audio": _create_anki_audio(note_to_add.audio_file_path),
        }
        notes.append(note)

    which_ones_can_be_added = _check_which_notes_can_be_added(notes)

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

    request_json = {
        "action": "addNotes",
        "version": 6,
        "params": {
            "notes": valid_notes,
        },
    }

    response = requests.post(anki_connect_url, json=request_json)
    response_json = response.json()
    added_note_ids = response_json["result"]

    if added_note_ids is None:
        print(f"Failed to add card to Anki deck. Error: {response_json['error']}")
    else:
        print(len(added_note_ids), " cards added to Anki deck")
    return added_note_ids


def _mark_notes_in_db(notes_to_add: list[AnkiNote], added_note_ids: list[int]):
    added_notes = anki_connector.get_notes(added_note_ids)
    for added_note in added_notes:
        for note_to_add in notes_to_add:
            if note_to_add.back == added_note["fields"]["Back"]["value"]:
                anki_id = added_note["noteId"]
                table_name = "vocabulary" if "word" in note_to_add.tags else "sentences"
                db_id = note_to_add.db_id
                vocabulary_connector.update_anki_note_id(table_name, db_id, anki_id)
                break


def add_notes_to_anki_and_mark_in_db(notes_to_add: list[AnkiNote]):

    added_note_ids = _add_notes_to_anki(notes_to_add)
    if added_note_ids is None:
        print("Anki adder returned to note ids. Skipping marking in DB")
    else:
        _mark_notes_in_db(notes_to_add, added_note_ids)


def make_sentence_note(sentence: JapaneseSentence):
    sentence_romaji = romanize_with_spaces(sentence.sentence)
    note_back = sentence.definition + "<br><br>" + sentence_romaji + "<br><br>Words:"
    for word in sentence.words:
        if word.reading is not None:
            word_romaji = romanize_with_spaces(word.reading)
            note_back += f"<br>{word_romaji} - {word.definition}"
        else:
            print(
                f"Warning: Word {word.word} has no reading. This will be skipped in the Anki note."
            )
    note = AnkiNote(sentence.audio_file_path, note_back, ["sentence"], sentence.db_id)
    return note


def add_words_and_sentences_to_anki(
    sentences: list[JapaneseSentence],
):  # MAKE SURE THE SENTENCE AND ALL THE WORds IN IT HAS DB IDS
    anki_connector._open_anki_if_not_running()
    notes: list[AnkiNote] = []
    for sentence in sentences:
        for word in sentence.words:
            if word.db_id is None:
                print(
                    f"Warning: Word {word.word} has no database ID. Skipping adding to Anki."
                )
                continue
            notes.append(
                AnkiNote(word.audio_file_path, word.definition, ["word"], word.db_id)
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
        sentence_note = make_sentence_note(sentence)
        notes.append(sentence_note)
    add_notes_to_anki_and_mark_in_db(notes)
