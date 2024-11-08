import sqlite3
from ..text_handling.japanese_word import JapaneseWord
from ..text_handling.sentence import JapaneseSentence


class WordDbConnector:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()

    def add_word_if_new(self, word: JapaneseWord):
        if not word.is_fully_defined():
            print(
                "ERROR: Word is not fully defined. Not adding to database. word: ",
                word.word,
                ", reading: ",
                word.reading,
                ", definition: ",
                word.definition,
                ", audio_file_path: ",
                word.audio_file_path,
            )
            return None
        if self._check_if_word_exists(word.word):
            self.cursor.execute(
                """
                SELECT * FROM vocabulary WHERE word = ?
                """,
                (word.word,),
            )
            word_data = self.cursor.fetchone()
            if word_data:
                word = JapaneseWord(
                    word_data[1],
                    word_data[2],
                    word_data[3],
                    word_data[4],
                    word_data[0],
                    word_data[5],
                )
                return word
            return None
        try:
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
        except sqlite3.Error as error:
            print("ERROR INSERTING WORD: ", error)
            return None

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
        words: list[JapaneseWord] = []
        for row in data:
            word = JapaneseWord(row[1], row[2], row[3], row[4], row[0], row[5])
            words.append(word)
        return words

    def get_words_without_anki_note_id(self):
        self.cursor.execute(
            """
            SELECT * FROM vocabulary WHERE anki_note_id IS NULL
            """
        )
        data = self.cursor.fetchall()
        words: list[JapaneseWord] = []
        for row in data:
            word = JapaneseWord(row[1], row[2], row[3], row[4], row[0])
            words.append(word)
        return words

    def get_words_for_sentence(self, sentence_id: int):
        self.cursor.execute(
            """
            SELECT word_id FROM sentences_words WHERE sentence_id = (?)
            """,
            (sentence_id,),
        )
        sentence_data = self.cursor.fetchall()
        word_ids = [row[0] for row in sentence_data]
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
        words: list[JapaneseWord] = []
        for row in word_data:
            word = JapaneseWord(row[1], row[2], row[3], row[4], row[0])
            words.append(word)
        return words

    def get_word_if_exists(self, word_in_kana: str):
        self.cursor.execute(
            """
                SELECT * FROM vocabulary WHERE word = (?)
            """,
            (word_in_kana,),
        )
        word_data = self.cursor.fetchone()
        if word_data is None:
            return None
        else:
            word = JapaneseWord(
                word_data[1], word_data[2], word_data[3], word_data[4], word_data[0]
            )
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
