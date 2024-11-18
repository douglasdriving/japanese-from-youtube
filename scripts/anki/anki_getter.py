from .anki_connector import AnkiConnector
import os


class AnkiGetter:

    connector = AnkiConnector()

    def __init__(self):
        pass

    def get_all_cards(self):
        card_ids = self.connector.post_request(
            "findCards", {"query": "deck:" + os.environ["ANKI_DECK_NAME"]}
        )
        cards = self.connector.post_request("cardsInfo", {"cards": card_ids})
        return cards

    def get_all_notes(self):
        ids = self.connector.post_request(
            "findNotes", {"query": "deck:" + os.environ["ANKI_DECK_NAME"]}
        )
        notes = self.get_notes(ids)
        return notes

    def get_notes(self, note_ids: list[int]):
        return self.connector.post_request("notesInfo", {"notes": note_ids})
