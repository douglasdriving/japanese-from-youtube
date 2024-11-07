import time
import subprocess
import requests
import os


class AnkiConnector:
    def __init__(self):
        pass

    def get_all_anki_cards(self):
        self._open_anki_if_not_running()
        card_ids = self._get_all_card_ids()
        cards = self._get_cards_info(card_ids)
        return cards

    def _open_anki_if_not_running(self):
        if not self._is_anki_running():
            print("Anki is not running. Opening Anki...")
            self._open_anki()
            while not self._is_anki_running():
                time.sleep(0.5)

    def _open_anki(self):
        try:
            subprocess.Popen([os.environ["ANKI_PATH"]])
            print("Opening Anki...")
        except Exception as e:
            print(f"Failed to open Anki: {e}")

    def _is_anki_running(self):
        try:
            response = requests.get(os.environ["ANKI_CONNECT_URL"])
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False

    def _get_all_card_ids(self):
        self._open_anki_if_not_running()
        anki_request_json = {
            "action": "findCards",
            "version": 6,
            "params": {"query": "deck:" + os.environ["ANKI_DECK_NAME"]},
        }
        response = requests.post(os.environ["ANKI_CONNECT_URL"], json=anki_request_json)
        response_json = response.json()
        result = response_json["result"]
        if result is None:
            print(f"Failed to retrieve all card ID's. Error: {response_json['error']}")
        return result

    def _get_cards_info(self, card_ids: list):
        self._open_anki_if_not_running()
        anki_request_json = {
            "action": "cardsInfo",
            "version": 6,
            "params": {"cards": card_ids},
        }
        response = requests.post(os.environ["ANKI_CONNECT_URL"], json=anki_request_json)
        response_json = response.json()
        result = response_json["result"]
        if result is None:
            print(f"Failed to retrieve data for cards. Error: {response_json['error']}")
        return result

    def update_card_back(self, note_id, new_back):
        self._open_anki_if_not_running()
        anki_request_json = {
            "action": "updateNoteFields",
            "version": 6,
            "params": {
                "note": {
                    "id": note_id,
                    "fields": {"Back": new_back},
                }
            },
        }
        response = requests.post(os.environ["ANKI_CONNECT_URL"], json=anki_request_json)
        response_json = response.json()
        result = response_json["result"]
        if response_json["error"] is not None:
            error = response_json["error"]
            print(f"Failed to update card with back: {new_back}. Error: {error}")
            return None
        else:
            print("Card updated successfully: ", note_id)
            return result

    def get_all_notes(self):
        self._open_anki_if_not_running()
        ids = self.get_all_note_ids()
        notes = self.get_notes(ids)
        return notes

    def get_notes(self, note_ids: list[int]):
        self._open_anki_if_not_running()
        anki_request_json = {
            "action": "notesInfo",
            "version": 6,
            "params": {"notes": note_ids},
        }
        response = requests.post(os.environ["ANKI_CONNECT_URL"], json=anki_request_json)
        response_json = response.json()
        result = response_json["result"]
        if result is None:
            print(f"Failed to retrieve notes. Error: {response_json['error']}")
        return result

    def get_all_note_ids(self):
        self._open_anki_if_not_running()
        anki_request_json = {
            "action": "findNotes",
            "version": 6,
            "params": {"query": "deck:" + os.environ["ANKI_DECK_NAME"]},
        }
        response = requests.post(os.environ["ANKI_CONNECT_URL"], json=anki_request_json)
        response_json = response.json()
        result = response_json["result"]
        if result is None:
            print(f"Failed to retrieve all note ID's. Error: {response_json['error']}")
        return result

    def tag_notes(self, note_ids: list[int], tag: str):
        print("Adding tag ", tag, " to notes: ", len(note_ids), "...")
        self._open_anki_if_not_running()
        anki_request_json = {
            "action": "addTags",
            "version": 6,
            "params": {
                "notes": note_ids,
                "tags": tag,
            },
        }
        response = requests.post(os.environ["ANKI_CONNECT_URL"], json=anki_request_json)
        response_json = response.json()
        result = response_json["result"]
        if response_json["error"] is not None:
            print(f"Failed to add tags to notes. Error: {response_json['error']}")
        else:
            print("Tags ", tag, " added successfully to notes: ", len(note_ids))
        return result

    def delete_notes(self, note_ids: list[int]):
        print("Deleting anki notes: ", len(note_ids), "...")
        self._open_anki_if_not_running()
        anki_request_json = {
            "action": "deleteNotes",
            "version": 6,
            "params": {"notes": note_ids},
        }
        response = requests.post(os.environ["ANKI_CONNECT_URL"], json=anki_request_json)
        response_json = response.json()
        if response_json["error"] is not None:
            print(f"Failed to delete notes. Error: {response_json['error']}")
        else:
            print("Anki notes deleted successfully: ", len(note_ids))
        return response_json["result"]
