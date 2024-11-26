from .word import JapaneseWord


class JapaneseSentence:

    sentence: str
    romaji: str
    definition: str
    audio_file_path: str
    db_id: int
    words: list[JapaneseWord]
    practice_interval: int
    anki_id: int
    gpt_generated: bool

    def __init__(
        self,
        sentence,
        definition: str = None,
        audio_file: str = None,
        database_id: int = None,
        words: list[JapaneseWord] = None,
        romaji: str = None,
        anki_id: int = None,
        practice_interval: int = 0,
        gpt_generated: bool = False,
    ):
        self.sentence = sentence
        self.definition = definition
        self.audio_file_path = audio_file
        self.db_id = database_id
        self.words = words
        self.practice_interval = practice_interval
        self.anki_id = anki_id
        self.romaji = romaji
        self.gpt_generated = gpt_generated

    def is_fully_defined(self):
        return (
            self.definition is not None
            and self.audio_file_path is not None
            and self.words is not None
            and self.romaji is not None
        )
