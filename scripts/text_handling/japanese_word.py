class JapaneseWord:

    word: str
    reading: str | None
    definition: str | None
    audio_file_path: str | None
    database_id: int | None

    def __init__(
        self,
        word: str,
        reading: str = None,
        definition: str = None,
        audio_file_path: str = None,
        database_id: int = None,
    ):
        self.word = word
        self.reading = reading
        self.definition = definition
        self.audio_file_path = audio_file_path
        self.database_id = database_id

    def is_same(self, other):
        is_same_word = self.word == other.word
        is_same_reading = self.reading == other.reading
        is_same_definition = self.definition == other.translation
        is_exact_same_word = is_same_word and is_same_reading and is_same_definition
        return is_exact_same_word

    def is_fully_defined(self):
        return (
            self.word != None
            and self.reading != None
            and self.definition != None
            and self.audio_file_path != None
        )
