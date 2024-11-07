from .db_connector import DbConnector
from ..text_handling.sentence import JapaneseSentence
import sqlite3


class VideoDbConnector:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()

    def get_locked_videos(self):
        self.cursor.execute(
            """
            SELECT * FROM videos WHERE unlocked = 0
            """
        )
        data = self.cursor.fetchall()
        return data

    def unlock_video(self, youtube_id: str):
        self.cursor.execute(
            """
            UPDATE videos SET unlocked = 1 WHERE youtube_id = ?
            """,
            (youtube_id,),
        )
        self.connection.commit()
        print(f"Unlocked video!!!!! -> https://www.youtube.com/watch?v={youtube_id}")

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
