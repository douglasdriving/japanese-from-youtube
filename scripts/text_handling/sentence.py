class JapaneseSentence:

    sentence: str
    definition: str
    audio_file_path: str

    def __init__(
        self,
        sentence,
        definition: str = None,
        audio_file: str = None,
    ):
        self.sentence = sentence
        self.definition = definition
        self.audio_file_path = audio_file

    def is_fully_defined(self):
        return self.definition is not None and self.audio_file_path is not None
