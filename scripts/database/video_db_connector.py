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

    # move this into sentence db connector when we got one
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

    def unlock_video(self, video_id: int):
        self.db_connector.cursor.execute(
            """
            UPDATE videos SET unlocked = 1 WHERE id = ?
            """,
            (video_id,),
        )
        self.db_connector.connection.commit()
