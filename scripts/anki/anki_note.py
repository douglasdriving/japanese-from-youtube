class AnkiNote:

    audio_file_path = None
    back = None

    def __init__(self, audio_file_path: str, back: str):
        self.audio_file_path = audio_file_path
        self.back = back
