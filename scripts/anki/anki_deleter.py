from .anki_connector import AnkiConnector


class AnkiDeleter:

    connector = AnkiConnector()

    def __init__(self):
        pass

    def delete_notes(self, note_ids: list[int]):
        print("Deleting anki notes: ", len(note_ids), "...")
        return self.connector.post_request("deleteNotes", {"notes": note_ids})
