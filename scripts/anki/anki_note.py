class AnkiNote:

    audio_file_path = None
    back = None
    tags = None

    def __init__(self, audio_file_path: str, back: str, tags: list[str] = []):
        self.audio_file_path = audio_file_path
        self.back = back
        self.tags = tags
