class JapaneseWord:

    word: str
    reading: str | None
    definition: str | None
    audio_file_path: str | None
    db_id: int | None
    anki_id: int | None
    practice_interval: int

    def __init__(
        self,
        word: str,
        reading: str = None,
        definition: str = None,
        audio_file_path: str = None,
        database_id: int = None,
        anki_id: int = None,
        practice_interval: int = 0,
    ):
        self.word = word
        self.reading = reading
        self.definition = definition
        self.audio_file_path = audio_file_path
        self.db_id = database_id
        self.anki_id = anki_id
        self.practice_interval = practice_interval

    def is_same(self, other):
        is_same_word = self.word == other.word
        is_same_reading = self.reading == other.reading
        is_same_definition = self.definition == other.translation
        is_exact_same_word = is_same_word and is_same_reading and is_same_definition
        return is_exact_same_word
