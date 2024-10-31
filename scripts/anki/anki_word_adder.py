import requests
import os
import subprocess
import time
import warnings
from .anki_note import AnkiNote
from ..text_handling.japanese_word import JapaneseWord
from ..text_handling.sentence import JapaneseSentence
from ..text_handling.romaziner import romanize_with_spaces

# could move this into env vars
deck_name = "jp_audio_cards"
anki_connect_url = "http://localhost:8765"
anki_path = r"C:\Users\dougl\AppData\Local\Programs\Anki\anki.exe"


def is_anki_running():
    try:
        response = requests.get("http://localhost:8765")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def open_anki():
    try:
        subprocess.Popen([anki_path])
        print("Opening Anki...")
    except Exception as e:
        print(f"Failed to open Anki: {e}")


def open_anki_if_not_running():
    if not is_anki_running():
        open_anki()
        time.sleep(3)


def get_card_options(deck_name):
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


def create_anki_audio(audio_file_path):
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


def create_add_note_request(deck_name, front, back, audio_file_path):
    card = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": "Basic",
                "fields": {"Front": front, "Back": back},
                "options": get_card_options(deck_name),
                "audio": create_anki_audio(audio_file_path),
            }
        },
    }
    return card


def add_card_to_anki(audio_file, translation):
    open_anki_if_not_running()
    card = create_add_note_request(deck_name, "", translation, audio_file)

    response = requests.post(anki_connect_url, json=card)
    response_json = response.json()
    if response_json["result"] is None:
        print(f"Failed to add card to Anki deck. Error: {response_json['error']}")
    else:
        print("Card added to Anki deck: " + audio_file + " (" + translation + ")")
    return response.json()


def check_which_notes_can_be_added(notes: list):
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


def add_notes_to_anki(cards: list[AnkiNote]):
    open_anki_if_not_running()

    notes = []
    for card in cards:
        note = {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {"Front": "", "Back": card.translation},
            "options": get_card_options(deck_name),
            "audio": create_anki_audio(card.audio_file_path),
        }
        notes.append(note)

    which_ones_can_be_added = check_which_notes_can_be_added(notes)

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

    if response_json["result"] is None:
        print(f"Failed to add card to Anki deck. Error: {response_json['error']}")
    else:
        print(len(valid_notes), " cards added to Anki deck")
    return response.json()


def make_sentence_note(sentence: JapaneseSentence):
    note_back = sentence.definition + "<br><br>Words:"
    for word in sentence.words:
        romaji = romanize_with_spaces(word.reading)
        note_back += f"<br>{romaji} - {word.definition}"
    note = AnkiNote(sentence.audio_file_path, note_back)
    return note


def add_words_and_sentences_to_anki(sentences: list[JapaneseSentence]):
    notes: list[AnkiNote] = []
    for sentence in sentences:
        for word in sentence.words:
            notes.append(AnkiNote(word.audio_file_path, word.definition))
        sentence_note = make_sentence_note(sentence)
        notes.append(sentence_note)
    add_notes_to_anki(notes)
