from ..text_handling.japanese_sentence import JapaneseSentence
from .word_db_connector import WordDbConnector
import sqlite3


class SentenceDbConnector:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor
    word_connector: WordDbConnector

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()
        self.word_connector = WordDbConnector()

    def add_sentence_if_new(self, sentence: JapaneseSentence):
        if not sentence.is_fully_defined():
            print("ERROR: Sentence is not fully defined. Not adding to database.")
            print(sentence)
            return None
        if self.check_if_sentence_exists(sentence.sentence):
            return None
        added_sentence = self._insert_sentence_in_db(sentence)
        return added_sentence

    def _insert_sentence_in_db(self, sentence: JapaneseSentence):
        try:
            self.cursor.execute(
                """
                INSERT INTO sentences (sentence, definition, audio_file_path)
                VALUES (?, ?, ?)
                """,
                (
                    sentence.sentence,
                    sentence.definition,
                    sentence.audio_file_path,
                ),
            )
            self.connection.commit()
            print(
                f"Added sentence '{sentence.sentence}' ({sentence.definition}) to database"
            )
            id = self.cursor.lastrowid
            sentence.db_id = id
            return sentence
        except sqlite3.Error as error:
            print("ERROR INSERTING SENTENCE: ", error)
            return None

    def check_if_sentence_exists(self, sentence):
        self.cursor.execute(
            """
            SELECT * FROM sentences WHERE sentence = (?)
            """,
            (sentence,),
        )
        return self.cursor.fetchone() is not None

    def get_all_sentences(self):
        self.cursor.execute(
            """
            SELECT * FROM sentences
            """
        )
        data = self.cursor.fetchall()
        sentences = self._make_sentences(data)
        return sentences

    def _make_sentences(self, table_data):
        sentences: list[JapaneseSentence] = []
        for row in table_data:
            sentence = self._make_sentence(row)
            sentences.append(sentence)
        return sentences

    def _make_sentence(self, table_row):
        sentence = JapaneseSentence(
            table_row[1], table_row[2], table_row[3], table_row[0], None, table_row[6]
        )
        sentence.anki_id = table_row[4]
        sentence.practice_interval = table_row[5]
        sentence.words = self.word_connector.get_words_for_sentence(sentence.db_id)
        return sentence

    def get_sentence_by_definition(self, english_sentence: str):
        self.cursor.execute(
            """
                SELECT * FROM sentences WHERE definition = (?)
            """,
            (english_sentence,),
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        else:
            sentence = self._make_sentence(row)
            return sentence

    def get_sentence_by_kana_text(self, kana_sentence: str):
        self.cursor.execute(
            """
                SELECT * FROM sentences WHERE sentence = (?)
            """,
            (kana_sentence,),
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        else:
            sentence = self._make_sentence(row)
            return sentence

    def get_sentences_without_anki_note_id(self):
        self.cursor.execute(
            """
            SELECT * FROM sentences WHERE anki_note_id IS NULL
            """
        )
        data = self.cursor.fetchall()
        sentences = self._make_sentences(data)
        return sentences

    def update_sentence_practice_intervals(self, sentences: list[JapaneseSentence]):
        for sentence in sentences:
            self.cursor.execute(
                """
                UPDATE sentences
                SET practice_interval = ?
                WHERE id = ?
                """,
                (sentence.practice_interval, sentence.db_id),
            )
            self.connection.commit()
            print(
                f"Updated practice interval for sentence {sentence.sentence} to {sentence.practice_interval}"
            )

    def add_sentence_word_crossref(self, sentence_id: int, word_id: int):
        try:
            self.cursor.execute(
                """
                INSERT INTO sentences_words (sentence_id, word_id)
                VALUES (?, ?)
                """,
                (sentence_id, word_id),
            )
            self.connection.commit()
            print(
                f"Added sentence-word crossref to database with sentence_id {sentence_id} and word_id {word_id}"
            )
        except sqlite3.Error as error:
            print("ERROR INSERTING SENTENCE WORD CROSSREF: ", error)

    def get_sentences_for_video(self, id: int):
        self.cursor.execute(
            """
            SELECT sentence_id FROM videos_sentences WHERE video_id = ?
            """,
            (id,),
        )
        sentence_ids = [row[0] for row in self.cursor.fetchall()]

        if not sentence_ids:
            return []

        self.cursor.execute(
            f"""
            SELECT * FROM sentences WHERE id IN ({','.join('?' for _ in sentence_ids)})
            """,
            sentence_ids,
        )
        data = self.cursor.fetchall()
        sentences = self._make_sentences(data)
        return sentences

    def update_audio_file_path(self, audio_file_path: str, sentence_id: int):
        self.cursor.execute(
            """
            UPDATE sentences
            SET audio_file_path = ?
            WHERE id = ?
            """,
            (audio_file_path, sentence_id),
        )
        self.connection.commit()
        print(
            f"Updated audio file path for sentence {sentence_id} to {audio_file_path}"
        )

    def delete_sentence(self, sentence_id: int):
        self.cursor.execute(
            """
            DELETE FROM sentences WHERE id = ?
            """,
            (sentence_id,),
        )
        self.connection.commit()
        print(f"Deleted sentence with id {sentence_id}")
