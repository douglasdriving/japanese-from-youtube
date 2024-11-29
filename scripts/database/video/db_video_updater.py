from ..db_connector import DbConnector


class DbVideoUpdater:
    connector = DbConnector()

    def __init__(self):
        pass

    def unlock_video(self, youtube_id: str):
        self.connector.cursor.execute(
            """
            UPDATE videos SET unlocked = 1 WHERE youtube_id = ?
            """,
            (youtube_id,),
        )
        self.connector.connection.commit()
        print(f"Unlocked video!!!!! -> https://www.youtube.com/watch?v={youtube_id}")
