import sqlite3
from ..text_handling.japanese_word import JapaneseWord
from ..text_handling.japanese_sentence import JapaneseSentence


class WordDbConnector:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()

    def add_word_if_new(self, word: JapaneseWord):

        if self._check_if_word_exists(word.word):
            return self._get_word(word.db_id)

        if not word.word:
            print("Word has no kana, cant add to database")
            return None

        if not word.definition:
            print("Warning: Word has no definition, cant insert into database")
            return None

        if not word.audio_file_path:
            print("Warning: Word has no audio file path, cant insert into database")
            return None

        if not word.reading:
            print("Warning: Word has no reading, will insert with kana as reading")
            word.reading = word.word

        try:
            word = self._add_word(word)
            return word
        except sqlite3.Error as error:
            print("ERROR INSERTING WORD: ", error)
            return None

    def _add_word(self, word: JapaneseWord):
        self.cursor.execute(
            """
            INSERT INTO vocabulary (word, reading, definition, audio_file_path)
            VALUES (?, ?, ?, ?)
            """,
            (word.word, word.reading, word.definition, word.audio_file_path),
        )
        self.connection.commit()
        print(f"Added word '{word.word}' ({word.definition}) to database")
        id = self.cursor.lastrowid
        word.db_id = id
        return word

    def _get_word(self, id: int):
        word = None
        self.cursor.execute(
            """
                SELECT * FROM vocabulary WHERE id = ?
                """,
            (id,),
        )
        row = self.cursor.fetchone()
        if row:
            word = self._make_word(row)
        return word

    def _check_if_word_exists(self, word_in_kanji: str):
        self.cursor.execute(
            """
            SELECT * FROM vocabulary WHERE word = (?)
            """,
            (word_in_kanji,),
        )
        word_exists = self.cursor.fetchone() is not None
        return word_exists

    def get_all_words(self):
        self.cursor.execute(
            """
            SELECT * FROM vocabulary
            """
        )
        data = self.cursor.fetchall()
        words = self._make_words(data)
        return words

    def _make_words(self, table_data):
        words: list[JapaneseWord] = []
        for row in table_data:
            word = self._make_word(row)
            words.append(word)
        return words

    def _make_word(self, row):
        word = JapaneseWord(row[1], row[2], row[3], row[4], row[0], row[5], row[6])
        return word

    def get_words_without_anki_note_id(self):
        self.cursor.execute(
            """
            SELECT * FROM vocabulary WHERE anki_note_id IS NULL
            """
        )
        data = self.cursor.fetchall()
        words = self._make_words(data)
        return words

    def get_words_for_sentence(self, sentence_id: int):
        self.cursor.execute(
            """
            SELECT word_id FROM sentences_words WHERE sentence_id = (?)
            """,
            (sentence_id,),
        )
        sentences_words_data = self.cursor.fetchall()
        word_ids = [row[0] for row in sentences_words_data]
        if len(word_ids) == 0:
            return []
        self.cursor.execute(
            """
            SELECT * FROM vocabulary WHERE id IN ({})
            """.format(
                ",".join("?" * len(word_ids))
            ),
            word_ids,
        )
        word_data = self.cursor.fetchall()
        words = self._make_words(word_data)
        return words

    def get_word_if_exists(self, word_in_kana: str):
        self.cursor.execute(
            """
                SELECT * FROM vocabulary WHERE word = (?)
            """,
            (word_in_kana,),
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        else:
            word = self._make_word(row)
            return word

    def update_anki_note_id(self, table_name: str, id: int, anki_id: int):
        self.cursor.execute(
            f"""
            UPDATE {table_name}
            SET anki_note_id = ?
            WHERE id = ?
            """,
            (anki_id, id),
        )
        self.connection.commit()
        print(f"Updated anki_note_id for {id} to {anki_id} in {table_name}")

    def update_word_practice_interval(self, word: JapaneseWord):
        self.cursor.execute(
            """
            UPDATE vocabulary
            SET practice_interval = ?
            WHERE id = ?
            """,
            (word.practice_interval, word.db_id),
        )
        self.connection.commit()
        print(
            f"Updated practice interval for {word.word} to {word.practice_interval} in database"
        )

    def update_audio_file_path(self, audio_file_path: str, word_id: int):
        self.cursor.execute(
            """
            UPDATE vocabulary
            SET audio_file_path = ?
            WHERE id = ?
            """,
            (audio_file_path, word_id),
        )
        self.connection.commit()
