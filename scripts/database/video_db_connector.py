from .db_connector import DbConnector
from ..text_handling.sentence import JapaneseSentence


class VideoDbConnector:

    db_connector: DbConnector

    def __init__(self):
        self.db_connector = DbConnector()

    def get_locked_videos(self):
        self.db_connector.cursor.execute(
            """
            SELECT * FROM videos WHERE unlocked = 0
            """
        )
        data = self.db_connector.cursor.fetchall()
        return data

    def get_sentences_for_video(self, video_id: int):
        self.db_connector.cursor.execute(
            """
            SELECT * FROM sentences WHERE video_id = ?
            """,
            (video_id,),
        )
        data = self.db_connector.cursor.fetchall()
        sentences: list[JapaneseSentence] = []
        for sentence_data in data:
            sentence = JapaneseSentence(
                sentence_data[1],
                sentence_data[2],
                sentence_data[3],
                sentence_data[0],
            )
            sentence.practice_interval = sentence_data[4]
            sentences.append(sentence)
        return sentences

    def unlock_video(self, video_id: int):
        self.db_connector.cursor.execute(
            """
            UPDATE videos SET unlocked = 1 WHERE id = ?
            """,
            (video_id,),
        )
        self.db_connector.connection.commit()
        print(f"Video with id {video_id} was unlocked!")
