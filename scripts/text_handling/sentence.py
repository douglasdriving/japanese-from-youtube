# hold data for a japanese sentence


class JapaneseSentence:
    def __init__(
        self,
        sentence,
        reading: str = None,
        definition: str = None,
        audio_file: str = None,
    ):
        self.sentence = sentence
        self.reading = reading
        self.definition = definition
        self.audio_file = audio_file

    def is_fully_defined(self):
        return (
            self.reading is not None
            and self.definition is not None
            and self.audio_file is not None
        )
