# extracts sentence data from a given japanese text
from .sentence import JapaneseSentence
from .speech_synthesizer import SpeechSynthesizer
from ..database.db_connector import DbConnector
from ..database.word.db_word_getter import DbWordGetter
from ..database.sentence.db_sentence_getter import DbSentenceGetter
from ..gpt.open_ai_connector import OpenAiConnector
from .word_extractor import WordExtractor
from .transcript_line import TranscriptLine


class SentenceExtractor:

    transcript: list[TranscriptLine]
    sentences: list[JapaneseSentence]
    db_connector: DbConnector
    word_extractor: WordExtractor
    speech_synthesizer: SpeechSynthesizer
    open_ai_connector: OpenAiConnector
    db_word_getter = DbWordGetter()
    db_sentence_getter = DbSentenceGetter()

    def __init__(self, transcript: list[TranscriptLine] = None):
        self.transcript = transcript
        self.sentences = []
        self.db_connector = DbConnector()
        self.word_extractor = WordExtractor()
        self.speech_synthesizer = SpeechSynthesizer()
        self.open_ai_connector = OpenAiConnector()

    def extract_sentences(self):
        print("Extracting sentences...")
        if self.transcript is None:
            print("ERROR: No text to extract sentences from")
            return None
        self._clean_lines()
        self._remove_empty_lines()
        print("Found ", len(self.transcript), " sentences in transcript")
        sentences_with_data: list[JapaneseSentence] = (
            self._make_sentences_from_transcript()
        )
        return sentences_with_data

    def extract_sentence(self, sentence_text: str):
        if sentence_text is None or sentence_text == "":
            print("ERROR: No text to extract sentence from")
            return None
        sentence_text = self._clean_line(sentence_text)
        sentence_in_db = self.db_sentence_getter.get_sentence_by_kana_text(
            sentence_text
        )
        if sentence_in_db is not None:
            print(
                "extracted sentence data from db: ",
                sentence_text,
            )
            return sentence_in_db
        else:
            created_sentence = self.create_new_sentence(sentence_text)
            print(
                "made new sentence: ",
                sentence_text,
                " (",
                created_sentence.definition,
                ")",
            )
            return created_sentence

    # TODO: start storing word-sentence connections, so that this can extract the words as well
    def extract_sentence_from_db_by_definition(self, english_sentence: str):
        japanese_sentence = self.db_sentence_getter.get_sentence_by_definition(
            english_sentence
        )
        if japanese_sentence is None:
            print("ERROR: Sentence not found in db: ", english_sentence)
            return None
        else:
            return japanese_sentence

    def _clean_lines(self):
        for line in self.transcript:
            line.text = self._clean_line(line.text)

    def _clean_line(self, line: str):
        line = "".join([char for char in line if ord(char) >= 128])
        line = line.replace("。", "")
        return line

    def _remove_empty_lines(self):
        self.transcript = [line for line in self.transcript if line.text.strip() != ""]

    def _turn_string_list_into_sentence_list(self, sentences_str: list[str]):
        sentences: list[JapaneseSentence] = []
        for sentence in sentences_str:
            sentences.append(JapaneseSentence(sentence))
        return sentences

    def _remove_lines_already_in_db(self):
        new_lines = []
        for line in self.transcript:
            print("checking if sentence exists: ", line.text, "...")
            if not self.db_sentence_getter.check_if_sentence_exists(line.text):
                print("sentence does not exist - adding it!")
                new_lines.append(line)
        self.transcript = new_lines

    def _make_sentences_from_transcript(self):
        print("making ", len(self.transcript), " sentences")
        sentences: list[JapaneseSentence] = []
        for idx, line in enumerate(self.transcript):
            sentence_in_db = self.db_sentence_getter.get_sentence_by_kana_text(
                line.text
            )
            if sentence_in_db is not None:
                print(
                    idx + 1,
                    ". extracted sentence data from db: ",
                    line.text,
                )
                sentences.append(sentence_in_db)
            else:
                created_sentence = self.create_new_sentence(line.text)
                print(
                    idx + 1,
                    ". made new sentence: ",
                    line.text,
                    " (",
                    created_sentence.definition,
                    ")",
                )
                sentences.append(sentence_in_db)
        return sentences

    def create_new_sentence(self, sentence_text):
        sentence_obj = self.open_ai_connector.get_sentence_data(sentence_text)
        if sentence_obj is None:
            print(
                "ERROR MAKING SENTENCE: ",
                sentence_text,
                " open ai connector returned none",
            )
            return None
        self._create_audio_for_sentence(sentence_obj)
        for word in sentence_obj.words:
            word_in_db = self.db_word_getter.get_word_if_exists(
                word_in_kana=word.word, reading=word.reading
            )
            if word_in_db is not None:
                word.db_id = word_in_db.db_id
                word.anki_id = word_in_db.anki_id
            if word_in_db is not None and word_in_db.audio_file_path is not None:
                word.audio_file_path = word_in_db.audio_file_path
            else:
                word.audio_file_path = self.speech_synthesizer.save_jp_text_as_audio(
                    word.reading, is_sentence=False
                )
        return sentence_obj

    def _create_audio_for_sentence(self, sentence_obj: JapaneseSentence):
        sentence_obj.audio_file_path = self.speech_synthesizer.save_jp_text_as_audio(
            sentence_obj.sentence, is_sentence=True
        )
