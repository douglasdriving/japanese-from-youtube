import sqlite3
import re
import os
from scripts.text_handling.speech_synthesis import save_jp_text_as_audio


class DataCleaner:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()

    def clean_database(self):
        self._clean_audio_file_names()

    def _clean_audio_file_names(self):
        self._clean_audio_file_names_in_table("vocabulary")
        self._clean_audio_file_names_in_table("sentences")

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
                new_audio_file = save_jp_text_as_audio(text, id, table == "sentences")
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
