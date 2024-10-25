import time
import subprocess
import requests
import os
import json


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


# Example of card info:
# {
#     "cardId": 1729315031890,
#     "fields": {
#         "Front": {"value": "[sound:s1.wav]", "order": 0},
#         "Back": {"value": "this is a test card!", "order": 1},
#     },
#     "fieldOrder": 0,
#     "question": "<style>.card {\n    font-family: arial;\n    font-size: 20px;\n    text-align: center;\n    color: black;\n    background-color: white;\n}\n</style>[anki:play:q:0]",
#     "answer": "<style>.card {\n    font-family: arial;\n    font-size: 20px;\n    text-align: center;\n    color: black;\n    background-color: white;\n}\n</style>[anki:play:q:0]\n\n<hr id=answer>\n\nthis is a test card!",
#     "modelName": "Basic",
#     "ord": 0,
#     "deckName": "jp_audio_cards",
#     "css": ".card {\n    font-family: arial;\n    font-size: 20px;\n    text-align: center;\n    color: black;\n    background-color: white;\n}\n",
#     "factor": 2500,
#     "interval": 2,
#     "note": 1729315031889,
#     "type": 2,
#     "queue": 2,
#     "due": 58,
#     "reps": 1,
#     "lapses": 0,
#     "left": 0,
#     "mod": 1729379914,
#     "nextReviews": [
#         "<\u206810\u2069m",
#         "\u20681\u2069d",
#         "\u20682\u2069d",
#         "\u20684\u2069d",
#     ],
# }