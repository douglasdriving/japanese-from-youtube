# extracts sentence data from a given japanese text
from .sentence import JapaneseSentence
from .speech_synthesizer import SpeechSynthesizer
from ..database.word_db_connector import WordDbConnector
from .translator import Translator
from .word_extractor import WordExtractor
from .transcript_line import TranscriptLine
from ..database.sentence_db_connector import SentenceDbConnector


class SentenceExtractor:

    transcript: list[TranscriptLine]
    sentences: list[JapaneseSentence]
    vocabulary_connector: WordDbConnector
    word_extractor: WordExtractor
    speech_synthesizer: SpeechSynthesizer
    sentence_db_connector: SentenceDbConnector

    def __init__(self, transcript: list[TranscriptLine]):
        self.transcript = transcript
        self.sentences = []
        self.vocabulary_connector = WordDbConnector()
        self.word_extractor = WordExtractor()
        self.speech_synthesizer = SpeechSynthesizer()
        self.sentence_db_connector = SentenceDbConnector()

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

    def extract_sentence_from_db_by_definition(self, english_sentence: str):
        # want a bulk version of this
        # requires bulk retrieval of sentences from db
        japanese_sentence = self.sentence_db_connector.get_sentence_by_definition(
            english_sentence
        )
        if japanese_sentence is None:
            print("ERROR: Sentence not found in db: ", english_sentence)
            return None
        else:
            # want a bulk version
            # what i need is a cross ref table for words and sentences
            japanese_sentence.words = self._extract_words_for_sentence(
                japanese_sentence
            )
            return japanese_sentence

    def _extract_sentence_from_db_by_kana(self, kana_sentence: str):
        japanese_sentence = self.sentence_db_connector.get_sentence_by_kana_text(
            kana_sentence
        )
        if japanese_sentence is None:
            print("ERROR: Sentence not found in db: ", kana_sentence)
            return None
        else:
            japanese_sentence.words = self._extract_words_for_sentence(
                japanese_sentence
            )
            return japanese_sentence

    def _clean_lines(self):
        for line in self.transcript:
            line.text = "".join([char for char in line.text if ord(char) >= 128])
            line.text = line.text.replace("。", "")  # also do this in data cleaner!

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
            if not self.sentence_db_connector.check_if_sentence_exists(line.text):
                print("sentence does not exist - adding it!")
                new_lines.append(line)
        self.transcript = new_lines

    def _make_sentences_from_transcript(self):
        print("making ", len(self.transcript), " sentences")
        sentences_with_definition: list[JapaneseSentence] = []
        for idx, line in enumerate(self.transcript):
            sentence_exists = self.sentence_db_connector.check_if_sentence_exists(
                line.text
            )
            if sentence_exists:
                print(
                    idx + 1,
                    ". extracting sentence data from db: ",
                    line.text,
                )
                sentence_obj = self._extract_sentence_from_db_by_kana(line.text)
                sentences_with_definition.append(sentence_obj)
            else:
                sentence_obj = self._make_sentence(line.text)
                print(
                    idx + 1,
                    ". made new sentence: ",
                    line.text,
                    " (",
                    sentence_obj.definition,
                    ")",
                )
                sentences_with_definition.append(sentence_obj)
        return sentences_with_definition

    def _make_sentence(self, sentence):  # this could be done as a batch
        translator = Translator()
        translation = translator.translate_jp_to_en(
            sentence
        )  # deepl can translate an array of sentences
        sentence_obj = JapaneseSentence(sentence, translation)
        sentence_obj.audio_file_path = self.speech_synthesizer.save_jp_text_as_audio(  # although, unclear if the azure api can do batch call. can we make parralel calls?
            sentence_obj.sentence, is_sentence=True
        )
        sentence_obj.words = self._extract_words_for_sentence(
            sentence_obj
        )  # and then this would be quite complicated to do as a batch as well.
        return sentence_obj

    def _extract_words_for_sentence(self, sentence: JapaneseSentence):
        words = self.word_extractor.extract_words_from_text(sentence.sentence)
        return words
