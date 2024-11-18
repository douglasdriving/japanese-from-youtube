import time
import subprocess
import requests
import os


class AnkiConnector:

    def __init__(self):
        pass

    def open_anki_if_not_running(self):
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

    # TODO: apply this everywhere
    def post_request(self, action: str, params: dict = {}):
        self.open_anki_if_not_running()
        params.setdefault("deck", os.environ["ANKI_DECK_NAME"])
        request_json = {
            "action": action,
            "version": 6,
            "params": params,
        }
        response = requests.post(os.environ["ANKI_CONNECT_URL"], json=request_json)
        response_json = response.json()
        result = response_json["result"]
        if result is None:
            print(
                f"Failed to make Anki request. Action: {action}, Params: {params}, Error: {response_json['error']}"
            )
        return result

    def update_card_back(self, note_id, new_back):
        return self.post_request(
            "updateNoteFields",
            {
                "note": {
                    "id": note_id,
                    "fields": {"Back": new_back},
                }
            },
        )

    # TODO: create note tagger class
    def tag_notes(self, note_ids: list[int], tag: str):
        print("Adding tag ", tag, " to notes: ", len(note_ids), "...")
        return self.post_request("addTags", {"notes": note_ids, "tags": tag})

    # TODO: create note deleter class
    def delete_notes(self, note_ids: list[int]):
        print("Deleting anki notes: ", len(note_ids), "...")
        return self.post_request("deleteNotes", {"notes": note_ids})
