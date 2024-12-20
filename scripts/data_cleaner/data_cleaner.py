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
from ..word_sorter.word_sorter import WordSorter
from datetime import datetime


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
    word_sorter = WordSorter()

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()
        self.db_connector = DbConnector()
        self.anki_connector = AnkiConnector()

    def clean_data_if_needed(self):
        last_clean_date = self._get_last_clean_date()
        print("Last clean date:", last_clean_date)
        if last_clean_date and (datetime.now() - last_clean_date).days < 7:
            print("Data clean not needed. Last clean was within 7 days.")
            return

        print("Cleaning data...")
        self._perform_data_cleaning()
        self._set_last_clean_date()

    def _get_last_clean_date(self):
        last_clean_file = os.path.join(os.path.dirname(__file__), "last_clean.txt")
        if os.path.exists(last_clean_file):
            with open(last_clean_file, "r") as file:
                date_str = file.read().strip()
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    print("Could not parse last clean date from file")
                    return None
        return None

    def _set_last_clean_date(self):
        last_clean_file = os.path.join(os.path.dirname(__file__), "last_clean.txt")
        with open(last_clean_file, "w") as file:
            file.write(datetime.now().strftime("%Y-%m-%d"))

    def _perform_data_cleaning(self):
        self._clean_audio_file_names()
        self._replace_sentences_with_gpt()
        self._add_missing_romaji()
        self._add_missing_crossrefs()
        self.delete_words_with_no_sentence_connection()
        self._clean_anki()
        self._add_missing_anki_ids()
        self._sort_words()

    def _replace_sentences_with_gpt(self):
        gpt_sentence_replacer = GPTSentenceReplacer()
        gpt_sentence_replacer.replace_sentences_not_genereated_with_gpt()

    def _add_missing_romaji(self):
        self.romaji_adder.add_missing_romaji()

    def _add_missing_crossrefs(self):
        self.crossref_adder.add_missing_crossrefs()

    def _clean_anki(self):
        anki_cleaner = AnkiCleaner()
        anki_cleaner.clean()

    def _sort_words(self):
        self.word_sorter.sort_words()

    def _clean_audio_file_names(self):
        print("Cleaning audio file names...")
        self._clean_audio_file_names_in_table("vocabulary")
        self._clean_audio_file_names_in_table("sentences")
        self._delete_all_audio_files_with_wrong_pattern()

    def _clean_audio_file_names_in_table(self, table="vocabulary"):

        data = (
            self.db_word_getter.get_all_words()
            if table == "vocabulary"
            else self.db_sentence_getter.get_all_sentences()
        )

        corrent_audio_file_patter = (
            re.compile(r"./audios/w\d+\.wav")
            if table == "vocabulary"
            else re.compile(r"./audios/s\d+\.wav")
        )

        for word_or_sentence in data:
            id = word_or_sentence.db_id
            text = (
                word_or_sentence.word
                if table == "vocabulary"
                else word_or_sentence.sentence
            )
            audio_file_path = word_or_sentence.audio_file_path
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
