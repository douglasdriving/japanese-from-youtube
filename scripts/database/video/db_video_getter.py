from ..db_connector import DbConnector


class VideoDbGetter:

    connector = DbConnector()

    def __init__(self):
        pass

    def get_locked_videos(self):
        self.connector.cursor.execute(
            """
            SELECT * FROM videos WHERE unlocked = 0
            """
        )
        data = self.connector.cursor.fetchall()
        return data
