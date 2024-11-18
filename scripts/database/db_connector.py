import sqlite3
from ..text_handling.word import JapaneseWord
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
            print(
                "ERROR: Sentence is not fully defined. Not adding to database: ",
                sentence.sentence,
                sentence.definition,
                sentence.audio_file_path,
                sentence.words,
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
                INSERT INTO sentences (sentence, definition, audio_file_path, gpt_generated)
                VALUES (?, ?, ?, ?)
                """,
                (
                    sentence.sentence,
                    sentence.definition,
                    sentence.audio_file_path,
                    sentence.gpt_generated,
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
            return self._turn_sentence_data_into_sentence(sentence_data)

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
    def turn_word_data_into_word(self, word_data):
        return JapaneseWord(
            word_data[1],
            word_data[2],
            word_data[3],
            word_data[4],
            word_data[0],
            word_data[5],
        )

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

    def update_sentence(self, sentence: JapaneseSentence):
        try:
            self.cursor.execute(
                """
                    UPDATE sentences
                    SET sentence = ?, definition = ?, audio_file_path = ?, gpt_generated = ?
                    WHERE id = ?
                    """,
                (
                    sentence.sentence,
                    sentence.definition,
                    sentence.audio_file_path,
                    sentence.gpt_generated,
                    sentence.db_id,
                ),
            )
            self.connection.commit()
            print(
                f"Updated sentence with id {sentence.db_id} to '{sentence.sentence}', '{sentence.definition}', '{sentence.audio_file_path}', '{sentence.gpt_generated}'"
            )
        except sqlite3.Error as error:
            print("ERROR UPDATING SENTENCE: ", error)
