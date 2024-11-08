import sqlite3
import re
import os
from scripts.text_handling.speech_synthesizer import SpeechSynthesizer
from .anki_cleaner import AnkiCleaner
from ..database.word_db_connector import WordDbConnector
from ..anki.anki_connector import AnkiConnector
from ..text_handling.word_extractor import WordExtractor
from ..text_handling.japanese_word import JapaneseWord
from ..database.sentence_db_connector import SentenceDbConnector


class DataCleaner:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor
    vocabulary_connector: WordDbConnector
    anki_connector: AnkiConnector
    sentence_db_connector: SentenceDbConnector

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()
        self.vocabulary_connector = WordDbConnector()
        self.anki_connector = AnkiConnector()
        self.sentence_db_connector = SentenceDbConnector()

    def clean_data(self):
        print("Cleaning data...")
        self._add_missing_crossrefs()
        self._clean_audio_file_names()
        anki_cleaner = AnkiCleaner()
        anki_cleaner.clean()
        self._add_missing_anki_ids()

    def _clean_audio_file_names(self):
        print("Cleaning audio file names...")
        self._clean_audio_file_names_in_table("vocabulary")
        self._clean_audio_file_names_in_table("sentences")
        self._delete_all_audio_files_with_wrong_pattern()

    def _clean_audio_file_names_in_table(self, table="vocabulary"):

        data = (
            self.vocabulary_connector.get_all_words()
            if table == "vocabulary"
            else self.sentence_db_connector.get_all_sentences()
        )

        corrent_audio_file_patter = (
            re.compile(r"./audios/w\d+\.wav")
            if table == "vocabulary"
            else re.compile(r"./audios/s\d+\.wav")
        )

        for entry in data:
            id = entry[0]
            text = entry[1]
            audio_file_path = entry[4] if table == "vocabulary" else entry[3]
            if not os.path.exists(audio_file_path):
                synthesizer = SpeechSynthesizer()
                new_audio_file = synthesizer.save_jp_text_as_audio(
                    text, id, table == "sentences"
                )
                self.cursor.execute(
                    f"""
                    UPDATE {table}
                    SET audio_file_path = ?
                    WHERE id = ?
                    """,
                    (new_audio_file, id),
                )
                self.connection.commit()
                print(f"Added audio file for {text} to {new_audio_file}")
            elif not corrent_audio_file_patter.match(audio_file_path):
                signifier = "s" if table == "sentences" else "w"
                new_file_path = f"./audios/{signifier}{id}.wav"
                table_name = "sentences" if table == "sentences" else "vocabulary"
                self.cursor.execute(
                    f"""
                    UPDATE {table_name}
                    SET audio_file_path = ?
                    WHERE id = ?
                    """,
                    (new_file_path, id),
                )
                self.connection.commit()
                os.rename(audio_file_path, new_file_path)
                print(f"Renamed {audio_file_path} to {new_file_path}")

    def _delete_all_audio_files_with_wrong_pattern(self):
        audio_files = os.listdir("./audios")
        for audio_file in audio_files:
            if not re.match(r"s\d+\.wav", audio_file) and not re.match(
                r"w\d+\.wav", audio_file
            ):
                os.remove(f"./audios/{audio_file}")
                print(
                    f"Deleted {audio_file} from audios folder since it is not in correct format"
                )

    def _add_missing_anki_ids(self):

        def update_words(all_anki_notes):
            print("Updating words...")
            words_to_update = self.vocabulary_connector.get_words_without_anki_note_id()
            for word in words_to_update:
                anki_note = next(
                    (
                        note
                        for note in all_anki_notes
                        if note["fields"]["Back"]["value"] == word.definition
                    ),
                    None,
                )
                if anki_note is None:
                    print(
                        f"Could not find anki note for word: {word.definition}, unable to update anki id"
                    )
                else:
                    anki_id = anki_note["noteId"]
                    self.vocabulary_connector.update_anki_note_id(
                        "vocabulary", word.db_id, anki_id
                    )

        def update_sentences(all_anki_notes):
            print("Updating sentences...")
            sentences_to_update = (
                self.sentence_db_connector.get_sentences_without_anki_note_id()
            )
            for sentence in sentences_to_update:
                anki_note = next(
                    (
                        note
                        for note in all_anki_notes
                        if note["fields"]["Back"]["value"]
                        .split("\n")[0]
                        .split("<br>")[0]
                        == sentence.definition
                    ),
                    None,
                )
                if anki_note is None:
                    print(
                        f"Could not find anki note for sentence: {sentence.definition}, unable to update anki id"
                    )
                else:
                    anki_id = anki_note["noteId"]
                    self.vocabulary_connector.update_anki_note_id(
                        "sentences", sentence.db_id, anki_id
                    )

        print("Adding missing anki ids...")
        anki_notes = self.anki_connector.get_all_notes()
        update_words(anki_notes)
        update_sentences(anki_notes)

    def _add_missing_crossrefs(self):
        sentences = self.sentence_db_connector.get_all_sentences()
        word_extractor = WordExtractor()
        for sentence in sentences:
            is_missing_crossrefs = sentence.words is None or len(sentence.words) == 0
            if is_missing_crossrefs:
                words: list[JapaneseWord] = word_extractor.extract_words_from_text(
                    sentence.sentence
                )
                for word in words:
                    if word.db_id is None:
                        word = self.vocabulary_connector.add_word_if_new(word)
                    if not word:
                        print(f"Could not add word because it is None")
                    elif word.db_id is not None:
                        self.sentence_db_connector.add_sentence_word_crossref(
                            sentence.db_id, word.db_id
                        )
                    else:
                        print(
                            f"Could not add crossref for word: {word.word} because it does not have a db id"
                        )
