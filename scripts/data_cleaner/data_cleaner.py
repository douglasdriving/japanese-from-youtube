import sqlite3
import re
import os
from scripts.text_handling.speech_synthesizer import SpeechSynthesizer
from .anki_cleaner import AnkiCleaner
from ..database.db_connector import DbConnector
from ..database.word.db_word_updater import DbWordUpdater
from ..database.word.db_word_getter import DbWordGetter
from ..database.word.db_word_deleter import DbWordDeleter
from ..database.sentence.db_sentence_getter import DbSentenceGetter
from ..anki.anki_connector import AnkiConnector
from ..anki.anki_getter import AnkiGetter
from ..anki.anki_deleter import AnkiDeleter
from .gpt_sentence_replacer import GPTSentenceReplacer
from .romaji_adder import RomajiAdder
from .crossref_adder import CrossrefAdder


class DataCleaner:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor
    db_connector: DbConnector
    anki_connector: AnkiConnector
    anki_getter = AnkiGetter()
    anki_deleter = AnkiDeleter()
    romaji_adder = RomajiAdder()
    crossref_adder = CrossrefAdder()
    db_word_updater = DbWordUpdater()
    db_word_getter = DbWordGetter()
    db_word_deleter = DbWordDeleter()
    db_sentence_getter = DbSentenceGetter()

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()
        self.db_connector = DbConnector()
        self.anki_connector = AnkiConnector()

    def clean_data(self):
        print("Cleaning data...")
        self._clean_audio_file_names()
        gpt_sentence_replacer = GPTSentenceReplacer()
        gpt_sentence_replacer.replace_sentences_not_genereated_with_gpt()
        self.romaji_adder.add_missing_sentence_romaji()
        self.crossref_adder.add_missing_crossrefs()
        self.delete_words_with_no_sentence_connection()
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
            self._get_all_words_from_db()
            if table == "vocabulary"
            else self._get_all_sentences_from_db()
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

    def _get_all_words_from_db(self):
        self.cursor.execute(
            """
            SELECT * FROM vocabulary
            """
        )
        return self.cursor.fetchall()

    def _get_all_sentences_from_db(self):
        self.cursor.execute(
            """
            SELECT * FROM sentences
            """
        )
        return self.cursor.fetchall()

    def delete_words_with_no_sentence_connection(self):
        words_without_crossrefs = self.db_word_getter.get_words_with_no_crossrefs()
        if len(words_without_crossrefs) == 0:
            return
        print(
            "Deleting",
            len(words_without_crossrefs),
            " words without sentence connection...",
        )
        db_ids = [word.db_id for word in words_without_crossrefs]
        self.db_word_deleter.delete_words(db_ids)
        anki_ids = [word.anki_id for word in words_without_crossrefs]
        self.anki_deleter.delete_notes(anki_ids)

    def _add_missing_anki_ids(self):

        def update_words(all_anki_notes):
            print("Updating words...")
            words_to_update = self.db_word_getter.get_words_without_anki_note_id()
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
                    self.db_word_updater.update_anki_note_id(
                        "vocabulary", word.db_id, anki_id
                    )

        def update_sentences(all_anki_notes):
            print("Updating sentences...")
            sentences_to_update = (
                self.db_sentence_getter.get_unlocked_sentences_without_anki_note_id()
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
                    self.db_word_updater.update_anki_note_id(
                        "sentences", sentence.db_id, anki_id
                    )

        print("Adding missing anki ids...")
        anki_notes = self.anki_getter.get_all_notes()
        update_words(anki_notes)
        update_sentences(anki_notes)
