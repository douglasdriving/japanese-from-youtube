import sqlite3
from ..text_handling.word import JapaneseWord
from ..text_handling.sentence import JapaneseSentence
from ..text_handling.romaziner import Romanizer

# TODO: refactor this, break into more classes


class DbConnector:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor
    romanizer = Romanizer()

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()

    # TODO: remove word getter functions
    def get_words_for_sentence(self, sentence_id: int):
        self.cursor.execute(
            """
            SELECT * FROM vocabulary
            JOIN words_sentences ON vocabulary.id = words_sentences.word_id
            WHERE words_sentences.sentence_id = (?)
            """,
            (sentence_id,),
        )
        data = self.cursor.fetchall()
        words: list[JapaneseWord] = []
        for row in data:
            word = self.turn_word_data_into_word(row)
            words.append(word)
        return words

    def turn_word_data_into_word(self, word_row):
        return JapaneseWord(
            database_id=word_row[0],
            word=word_row[1],
            reading=word_row[2],
            definition=word_row[3],
            audio_file_path=word_row[4],
            anki_id=word_row[5],
            romaji=word_row[6],
            practice_interval=word_row[7],
        )

    # sentence adder
    def add_sentence_if_new(self, sentence: JapaneseSentence):
        if not sentence.is_fully_defined():
            print(
                "ERROR: Sentence is not fully defined. Not adding to database: ",
                sentence.sentence,
                sentence.definition,
                sentence.audio_file_path,
                sentence.words,
                sentence.romaji,
            )
            return None
        if self.check_if_sentence_exists(sentence.sentence):
            return None
        added_sentence = self._insert_sentence_in_db(sentence)
        return added_sentence

    def _insert_sentence_in_db(self, sentence: JapaneseSentence):
        try:
            self.cursor.execute(
                """
                INSERT INTO sentences (sentence, definition, audio_file_path, gpt_generated, romaji)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    sentence.sentence,
                    sentence.definition,
                    sentence.audio_file_path,
                    sentence.gpt_generated,
                    sentence.romaji,
                ),
            )
            self.connection.commit()
            print(
                f"Added sentence '{sentence.romaji}' ({sentence.definition}) to database"
            )
            id = self.cursor.lastrowid
            sentence.db_id = id
            for word in sentence.words:
                self.insert_word_sentence_relation(word.db_id, sentence.db_id)
            return sentence
        except sqlite3.Error as error:
            print("ERROR INSERTING SENTENCE: ", error)
            return None

    def insert_word_sentence_relation(self, word_id: int, sentence_id: int):
        try:
            self.cursor.execute(
                """
                INSERT INTO words_sentences (word_id, sentence_id)
                VALUES (?, ?)
                """,
                (word_id, sentence_id),
            )
            self.connection.commit()
            print(
                f"Added word-sentence relation to database with word_id {word_id} and sentence_id {sentence_id}"
            )
        except sqlite3.Error as error:
            print("ERROR INSERTING WORD SENTENCE RELATION: ", error)

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
            sentences.append(self._turn_sentence_data_into_sentence(row))
        return sentences

    def get_sentences_not_generated_by_gpt(self):
        self.cursor.execute(
            """
            SELECT * FROM sentences WHERE gpt_generated = 0
            """
        )
        data = self.cursor.fetchall()
        sentences: list[JapaneseSentence] = []
        for row in data:
            sentences.append(self._turn_sentence_data_into_sentence(row))
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
            return self._turn_sentence_data_into_sentence(sentence_data)

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
            return self._turn_sentence_data_into_sentence(sentence_data)

    def get_sentences_without_romaji(self):
        self.cursor.execute(
            """
            SELECT * FROM sentences WHERE romaji IS NULL
            """
        )
        data = self.cursor.fetchall()
        sentences: list[JapaneseSentence] = []
        for row in data:
            sentences.append(self._turn_sentence_data_into_sentence(row))
        return sentences

    def get_sentences_without_word_crossrefs(self):
        self.cursor.execute(
            """
            SELECT * FROM sentences
            WHERE id NOT IN (
                SELECT sentence_id FROM words_sentences
            )
            """
        )
        data = self.cursor.fetchall()
        sentences: list[JapaneseSentence] = []
        for row in data:
            sentences.append(self._turn_sentence_data_into_sentence(row))
        return sentences

    def get_locked_sentences(self):
        self.cursor.execute(
            """
            SELECT * FROM sentences WHERE locked IS 1
            """
        )
        data = self.cursor.fetchall()
        sentences: list[JapaneseSentence] = []
        for row in data:
            sentences.append(self._turn_sentence_data_into_sentence(row))
        return sentences

    def add_crossref(self, word_id: int, sentence_id: int):
        try:
            self.cursor.execute(
                """
                INSERT INTO words_sentences (word_id, sentence_id)
                VALUES (?, ?)
                """,
                (word_id, sentence_id),
            )
            self.connection.commit()
            print(
                f"Added crossref between word with id {word_id} and sentence with id {sentence_id}"
            )
        except sqlite3.Error as error:
            print("ERROR ADDING CROSSREF: ", error)

    # TODO: make sure this function is used by all sentence extractions
    def _turn_sentence_data_into_sentence(self, sentence_data):
        sentence = JapaneseSentence(
            database_id=sentence_data[0],
            sentence=sentence_data[1],
            definition=sentence_data[2],
            audio_file=sentence_data[3],
            anki_id=sentence_data[4],
            practice_interval=sentence_data[5],
            gpt_generated=sentence_data[6],
            romaji=sentence_data[7],
            words=self.get_words_for_sentence(
                sentence_data[0]
            ),  # TODO: replace with getter class function
            locked=(sentence_data[8] == 1),
        )
        # TODO: when this is iterated over every sentence in th db, that leads to a lot of requests. instead, get all words from db and match them to the sentence
        return sentence

    def get_unlocked_sentences_without_anki_note_id(self):
        self.cursor.execute(
            """
            SELECT * FROM sentences WHERE anki_note_id IS NULL AND locked = 0
            """
        )
        data = self.cursor.fetchall()
        sentences: list[JapaneseSentence] = []
        for row in data:
            sentence = JapaneseSentence(row[1], row[2], row[3], row[0])
            sentences.append(sentence)
        return sentences

    # video adder
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

    # deleter
    def delete_sentence(self, sentence_id: int):
        try:
            self.cursor.execute(
                """
                DELETE FROM sentences
                WHERE id = ?
                """,
                (sentence_id,),
            )
            self.connection.commit()
            print(f"Deleted sentence with id {sentence_id}")
        except sqlite3.Error as error:
            print("ERROR DELETING SENTENCE: ", error)

    def delete_words(self, ids: list[int]):
        try:
            self.cursor.executemany(
                """
            DELETE FROM vocabulary
            WHERE id = ?
            """,
                [(id,) for id in ids],
            )
            self.connection.commit()
            print(f"Deleted words with ids: {ids}")
        except sqlite3.Error as error:
            print("ERROR DELETING WORDS: ", error)

    # sentence updater
    def unlock_sentence(self, sentence_id: int):
        try:
            self.cursor.execute(
                """
                UPDATE sentences
                SET locked = 0
                WHERE id = ?
                """,
                (sentence_id,),
            )
            self.connection.commit()
            print(f"unlocked sentence with ids: {sentence_id}")
        except sqlite3.Error as error:
            print("ERROR UNLOCKING SENTENCE: ", error)

    def remove_anki_id_from_sentence(self, sentence_id: int):
        try:
            self.cursor.execute(
                """
                UPDATE sentences
                SET anki_note_id = NULL
                WHERE id = ?
                """,
                (sentence_id,),
            )
            self.connection.commit()
            print(f"removed anki id from sentence with db id: ", sentence_id)
        except sqlite3.Error as error:
            print("ERROR REMOVE ANKI ID FROM SENTENCE: ", error)
