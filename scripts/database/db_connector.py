import sqlite3
from ..text_handling.japanese_word import JapaneseWord
from ..text_handling.sentence import JapaneseSentence

# time to refactor


class DbConnector:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()

    def add_word_if_new(self, word: JapaneseWord):
        if not word.is_fully_defined():
            print("ERROR: Word is not fully defined. Not adding to database.")
            print(word)
            return None
        if self._check_if_word_exists(word.word):
            print("skipping adding word to db since it already exists: ", word.word)
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

    def add_sentence_if_new(self, sentence: JapaneseSentence):
        if not sentence.is_fully_defined():
            print("ERROR: Sentence is not fully defined. Not adding to database.")
            print(sentence)
            return None
        if self.check_if_sentence_exists(sentence.sentence):
            print(
                "skipping adding sentence to db since it already exists: ",
                sentence.sentence,
            )
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

    def get_all_words(self):
        self.cursor.execute(
            """
            SELECT * FROM vocabulary
            """
        )
        data = self.cursor.fetchall()
        words: list[JapaneseWord] = []
        for row in data:
            word = JapaneseWord(row[1], row[2], row[3], row[4], row[0])
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
            sentence.anki_note_id = row[4]
            sentences.append(sentence)
        return sentences

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

    def add_video(self, youtube_id: str, title: str):
        try:
            # check if video already exists
            self.cursor.execute(
                """
                SELECT id FROM videos WHERE youtube_id = ?
                """,
                (youtube_id,),
            )
            video_data = self.cursor.fetchone()
            if video_data is not None:
                print(
                    f"Video with youtube_id '{youtube_id}' already exists with id {video_data[0]}"
                )
                id = video_data[0]
                return video_data[0]

            # otherwise, add video to db
            self.cursor.execute(
                """
                INSERT INTO videos (youtube_id, title)
                VALUES (?, ?)
                """,
                (youtube_id, title),
            )
            self.connection.commit()
            id = self.cursor.lastrowid
            print(f"Added video '{title}' to database with id {id}")
            return id
        except sqlite3.Error as error:
            print("ERROR INSERTING VIDEO: ", error)

    def add_video_sentences_crossref(self, video_id: int, sentence_id: int):
        try:
            self.cursor.execute(
                """
                INSERT INTO videos_sentences (video_id, sentence_id)
                VALUES (?, ?)
                """,
                (video_id, sentence_id),
            )
            self.connection.commit()
            print(
                f"Added video-sentence crossref to database with video_id {video_id} and sentence_id {sentence_id}"
            )
        except sqlite3.Error as error:
            print("ERROR INSERTING VIDEO SENTENCE CROSSREF: ", error)

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