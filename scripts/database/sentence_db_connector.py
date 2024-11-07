from ..text_handling.sentence import JapaneseSentence
import sqlite3


class SentenceDbConnector:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()

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
        sentences: list[JapaneseSentence] = []
        for row in data:
            sentence = JapaneseSentence(row[1], row[2], row[3], row[0])
            sentence.anki_id = row[4]
            sentence.practice_interval = row[5]
            sentences.append(sentence)
        for sentence in sentences:
            sentence.words = self.get_words_for_sentence(sentence.db_id)
        return sentences

    def get_sentence_by_definition(self, english_sentence: str):
        self.cursor.execute(
            """
                SELECT * FROM sentences WHERE definition = (?)
            """,
            (english_sentence,),
        )
        sentence_data = self.cursor.fetchone()
        if sentence_data is None:
            return None
        else:
            sentence = JapaneseSentence(
                sentence_data[1], sentence_data[2], sentence_data[3], sentence_data[0]
            )
            return sentence

    def get_sentence_by_kana_text(self, kana_sentence: str):
        self.cursor.execute(
            """
                SELECT * FROM sentences WHERE sentence = (?)
            """,
            (kana_sentence,),
        )
        sentence_data = self.cursor.fetchone()
        if sentence_data is None:
            return None
        else:
            sentence = JapaneseSentence(
                sentence_data[1], sentence_data[2], sentence_data[3], sentence_data[0]
            )
            return sentence

    def get_sentences_without_anki_note_id(self):
        self.cursor.execute(
            """
            SELECT * FROM sentences WHERE anki_note_id IS NULL
            """
        )
        data = self.cursor.fetchall()
        sentences: list[JapaneseSentence] = []
        for row in data:
            sentence = JapaneseSentence(row[1], row[2], row[3], row[0])
            sentences.append(sentence)
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
        self.db_connector.cursor.execute(
            """
            SELECT sentence_id FROM videos_sentences WHERE video_id = ?
            """,
            (id,),
        )
        sentence_ids = [row[0] for row in self.db_connector.cursor.fetchall()]

        if not sentence_ids:
            return []

        self.db_connector.cursor.execute(
            f"""
            SELECT * FROM sentences WHERE id IN ({','.join('?' for _ in sentence_ids)})
            """,
            sentence_ids,
        )
        data = self.db_connector.cursor.fetchall()
        # would be useful with a function that transforms the db data into a list of JapaneseSentence objects
        sentences: list[JapaneseSentence] = []
        for sentence_data in data:
            sentence = JapaneseSentence(
                sentence_data[1],
                sentence_data[2],
                sentence_data[3],
                sentence_data[0],
            )
            sentence.anki_id = sentence_data[4]
            sentence.practice_interval = sentence_data[5]
            sentences.append(sentence)
        return sentences
