class JapaneseSentence:

    sentence: str
    definition: str
    audio_file_path: str
    database_id: int

    def __init__(
        self,
        sentence,
        definition: str = None,
        audio_file: str = None,
        database_id: int = None,
    ):
        self.sentence = sentence
        self.definition = definition
        self.audio_file_path = audio_file
        self.database_id = database_id

    def is_fully_defined(self):
        return self.definition is not None and self.audio_file_path is not None
