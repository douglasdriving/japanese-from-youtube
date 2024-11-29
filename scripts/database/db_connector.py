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

    # word adder
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
            return word

        word_in_db = self.get_word_if_exists(word.word, word.reading)
        if word_in_db is not None:
            updated_definition = self._add_definition_to_word_if_new(
                word_id=word.db_id, new_definition=word.definition
            )
            word_in_db.definition = updated_definition
            return word_in_db

        try:
            self.cursor.execute(
                """
                    INSERT INTO vocabulary (word, reading, definition, audio_file_path, romaji)
                    VALUES (?, ?, ?, ?, ?)
                """,
                (
                    word.word,
                    word.reading,
                    word.definition,
                    word.audio_file_path,
                    word.romaji,
                ),
            )
            self.connection.commit()
            print(f"Added word '{word.romaji}' ({word.definition}) to database")
            id = self.cursor.lastrowid
            word.db_id = id
            return word
        except sqlite3.Error as error:
            print("ERROR INSERTING WORD: ", error)
            return None

    # word updater
    def _add_definition_to_word_if_new(self, word_id, new_definition: str):
        self.cursor.execute(
            """
            SELECT definition FROM vocabulary WHERE id = (?)
            """,
            (word_id,),
        )
        current_definition = self.cursor.fetchone()
        if current_definition is None:
            print(
                f"ERROR: Word with id {word_id} does not exist. cant update its definition"
            )
            return ""
        current_definition = current_definition[0]
        definitions = current_definition.split(";")
        for definition in definitions:
            if definition.strip() == new_definition.strip():
                return current_definition
        updated_definition = f"{current_definition}; {new_definition}"
        self.cursor.execute(
            """
            UPDATE vocabulary
            SET definition = ?
            WHERE id = ?
            """,
            (updated_definition, word_id),
        )
        self.connection.commit()
        print(f"Added definition '{new_definition}' to word with id {word_id}")
        return updated_definition

    # word getter
    def _check_if_word_exists(self, word_in_kanji: str):
        self.cursor.execute(
            """
            SELECT * FROM vocabulary WHERE word = (?)
            """,
            (word_in_kanji,),
        )
        word_exists = self.cursor.fetchone() is not None
        return word_exists

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

    # sentence adder
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

    # sentence adder
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

    # sentence getter
    def check_if_sentence_exists(self, sentence):
        self.cursor.execute(
            """
    SELECT * FROM sentences WHERE sentence = (?)
    """,
            (sentence,),
        )
        return self.cursor.fetchone() is not None

    # word getter
    def get_all_words(self):
        self.cursor.execute(
            """
            SELECT * FROM vocabulary
            """
        )
        data = self.cursor.fetchall()
        words: list[JapaneseWord] = []
        for row in data:
            word = self.turn_word_data_into_word(row)
            words.append(word)
        return words

    # word getter
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

    # word getter
    def get_words_with_no_crossrefs(self):
        self.cursor.execute(
            """
            SELECT * FROM vocabulary
            WHERE id NOT IN (
                SELECT word_id FROM words_sentences
            )
            """
        )
        data = self.cursor.fetchall()
        words: list[JapaneseWord] = []
        for row in data:
            words.append(self.turn_word_data_into_word(row))
        return words

    # word getter
    def get_words_without_progress(self):
        try:
            self.cursor.execute(
                """
                SELECT * FROM vocabulary WHERE practice_interval = 0
                """
            )
            data = self.cursor.fetchall()
            words: list[JapaneseWord] = []
            for row in data:
                words.append(self.turn_word_data_into_word(row))
            return words
        except sqlite3.Error as error:
            print("ERROR GETTING WORDS WITHOUT PROGRESS: ", error)
            return []

    # word getter
    def get_words_popilarity(self, words: list[JapaneseWord]):
        word_popularity = {}
        for word in words:
            word_popularity[word] = self.get_word_popularity(word)
        return word_popularity

    # word getter
    def get_word_popularity(self, word: JapaneseWord):
        self.cursor.execute(
            """
            SELECT * FROM words_sentences WHERE word_id = ?
            """,
            (word.db_id,),
        )
        data = self.cursor.fetchall()
        return len(data)

    # sentence getter
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

    # sentence getter
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

    # word getter
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
            return self.turn_word_data_into_word(word_data)

    # sentence getter
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

    # sentence getter
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

    # sentence getter
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

    # sentence getter
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

    # sentence getter
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

    # TODO: make sure this function is used by all sentence extractions
    # sentence getter
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
            words=self.get_words_for_sentence(sentence_data[0]),
            locked=(sentence_data[8] == 1),
        )
        # TODO: when this is iterated over every sentence in th db, that leads to a lot of requests. instead, get all words from db and match them to the sentence
        return sentence

    # word getter
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

    # sentence getter
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

    def update_anki_note_id(self, table_name: str, id: int, anki_id: int):
        if id is None:
            print(
                f"Warning: Sentence has no database ID. Skipping changing the anki ID."
            )
            return
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

    # video adder
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

    # word updater
    def update_word_practice_intervals(self, words: list[JapaneseWord]):
        for word in words:
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
                f"Updated practice interval for word {word.word} to {word.practice_interval}"
            )

    # word getter
    def get_word_if_exists(self, word_in_kana: str, reading: str):
        self.cursor.execute(
            """
                SELECT * FROM vocabulary WHERE word = (?) AND reading = (?)
            """,
            (word_in_kana, reading),
        )
        word_data = self.cursor.fetchone()
        if word_data is None:
            return None
        else:
            return self.turn_word_data_into_word(word_data)

    # TODO: make sure this function is used by all word extractions
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

    # word updater
    def change_word_definition(self, word_id: int, new_definition: str):
        try:
            self.cursor.execute(
                """
                    UPDATE vocabulary
                    SET definition = ?
                    WHERE id = ?
                    """,
                (new_definition, word_id),
            )
            self.connection.commit()
            print(
                f"Updated definition for word with id {word_id} to '{new_definition}'"
            )
        except sqlite3.Error as error:
            print("ERROR UPDATING WORD DEFINITION: ", error)

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

    # deleter
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

    # sentence adder
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

    # sentence updater
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
