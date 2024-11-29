from ..db_connector import DbConnector
import sqlite3


class DbVideoAdder:
    connector = DbConnector()

    def __init__(self):
        pass

    def add_video(self, youtube_id: str, title: str):
        try:
            # check if video already exists
            self.connector.cursor.execute(
                """
                SELECT id FROM videos WHERE youtube_id = ?
                """,
                (youtube_id,),
            )
            video_data = self.connector.cursor.fetchone()
            if video_data is not None:
                print(
                    f"Video with youtube_id '{youtube_id}' already exists with id {video_data[0]}"
                )
                id = video_data[0]
                return video_data[0]

            # otherwise, add video to db
            self.connector.cursor.execute(
                """
                INSERT INTO videos (youtube_id, title)
                VALUES (?, ?)
                """,
                (youtube_id, title),
            )
            self.connector.connection.commit()
            id = self.connector.cursor.lastrowid
            print(f"Added video '{title}' to database with id {id}")
            return id
        except sqlite3.Error as error:
            print("ERROR INSERTING VIDEO: ", error)

    def add_video_sentences_crossref(self, video_id: int, sentence_id: int):
        try:
            self.connector.cursor.execute(
                """
                INSERT INTO videos_sentences (video_id, sentence_id)
                VALUES (?, ?)
                """,
                (video_id, sentence_id),
            )
            self.connector.connection.commit()
            print(
                f"Added video-sentence crossref to database with video_id {video_id} and sentence_id {sentence_id}"
            )
        except sqlite3.Error as error:
            print("ERROR INSERTING VIDEO SENTENCE CROSSREF: ", error)
