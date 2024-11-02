class AnkiNote:

    audio_file_path = None
    back = None
    tags = None
    db_id = None

    def __init__(
        self,
        audio_file_path: str,
        back: str,
        tags: list[str] = [],
        db_id: int = None,
    ):
        self.audio_file_path = audio_file_path
        self.back = back
        self.tags = tags
        self.db_id = db_id
