from ..text_handling.sentence import JapaneseSentence
from ..text_handling.word import JapaneseWord
from .anki_note import AnkiNote


class AnkiNoteMaker:
    def __init__(self):
        pass

    def make_sentence_note(self, sentence: JapaneseSentence):
        note_back = (
            sentence.definition + "<br><br>" + sentence.romaji + "<br><br>Words:"
        )
        for word in sentence.words:
            if word.reading is not None:
                note_back += f"<br>{word.romaji} - {word.definition}"
            else:
                print(
                    f"Warning: Word {word.word} has no reading. This will be skipped in the Anki note."
                )
        note = AnkiNote(
            audio_file_path=sentence.audio_file_path,
            back=note_back,
            tags=["sentence"],
            db_id=sentence.db_id,
        )
        return note

    def make_word_note(self, word: JapaneseWord):

        def make_back_text(word: JapaneseWord):
            if word.romaji is not None:
                return word.romaji + " - " + word.definition
            return word.word + " - " + word.definition

        note = AnkiNote(
            audio_file_path=word.audio_file_path,
            back=make_back_text(word),
            tags=["word"],
            db_id=word.db_id,
        )
        return note
