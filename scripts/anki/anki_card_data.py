class AnkiCardData:

    audio_file_path = None
    translation = None

    def __init__(self, audio_file_path: str, translation: str):
        self.audio_file_path = audio_file_path
        self.translation = translation
