from .anki_connector import AnkiConnector
from .anki_adder import AnkiAdder
from ..text_handling.sentence import JapaneseSentence


class AnkiUpdater:
    connector = AnkiConnector()
    adder = AnkiAdder()

    def __init__(self):
        pass

    def update_card_back(self, note_id, new_back):
        return self.connector.post_request(
            "updateNoteFields",
            {
                "note": {
                    "id": note_id,
                    "fields": {"Back": new_back},
                }
            },
        )

    def update_sentence(self, sentence: JapaneseSentence):
        note = self.adder.make_sentence_note(sentence)
        note_id = sentence.anki_id
        new_back = note.back
        self.update_card_back(note_id, new_back)

    def tag_notes(self, note_ids: list[int], tag: str):
        print("Adding tag ", tag, " to notes: ", len(note_ids), "...")
        return self.post_request("addTags", {"notes": note_ids, "tags": tag})
