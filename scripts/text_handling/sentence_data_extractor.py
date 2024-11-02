# extracts sentence data from a given japanese text
from .sentence import JapaneseSentence
from .speech_synthesis import save_jp_text_as_audio
from ..database.vocabulary_connector import VocabularyConnector
from .translator import translate_jp_to_en
from .word_extractor_new import WordExtractor
from ..transcript_line import TranscriptLine


class SentenceDataExtractor:

    transcript: list[TranscriptLine]
    sentences: list[JapaneseSentence]
    vocabulary_connector: VocabularyConnector
    word_extractor: WordExtractor

    def __init__(self, transcript: list[TranscriptLine]):
        self.transcript = transcript
        self.sentences = []
        self.vocabulary_connector = VocabularyConnector()
        self.word_extractor = WordExtractor()

    def extract_sentences_not_in_db(self):
        print("Extracting sentences...")
        if self.transcript is None:
            print("ERROR: No text to extract sentences from")
            return None
        self.remove_latin_characters()
        self._remove_lines_already_in_db()
        print("Found ", len(self.transcript), " new sentences")
        sentences_with_data: list[JapaneseSentence] = (
            self._make_transcript_into_sentence_objects()
        )
        return sentences_with_data

    def extract_db_data_for_sentence(self, enlish_sentence: str):
        japanese_sentence = self.vocabulary_connector.get_sentence(enlish_sentence)
        if japanese_sentence is None:
            print("ERROR: Sentence not found in db: ", enlish_sentence)
            return None
        else:
            japanese_sentence.words = self._extract_words_for_sentence(
                japanese_sentence
            )
            return japanese_sentence

    def remove_latin_characters(self):
        for line in self.transcript:
            line.text = "".join([char for char in line.text if ord(char) >= 128])

    def _turn_string_list_into_sentence_list(self, sentences_str: list[str]):
        sentences: list[JapaneseSentence] = []
        for sentence in sentences_str:
            sentences.append(JapaneseSentence(sentence))
        return sentences

    # def _split_text_into_sentences(self):
    #     sentences = self.transcript.replace("。", " ").split(" ")
    #     sentences = [sentence for sentence in sentences if sentence != ""]
    #     return sentences

    def _remove_lines_already_in_db(self):
        self.transcript = [
            line
            for line in self.transcript
            if not self.vocabulary_connector.check_if_sentence_exists(line.text)
        ]

    def _make_transcript_into_sentence_objects(self):
        print("making ", len(self.transcript), " sentences")
        sentences_with_definition: list[JapaneseSentence] = []
        for idx, line in enumerate(self.transcript):
            sentence_exists = self.vocabulary_connector.check_if_sentence_exists(
                line.text
            )
            if sentence_exists:
                print(
                    idx + 1,
                    ". skipping sentence since it already exists: ",
                    line.text,
                )
            else:
                sentence_obj = self._make_sentence_object(line.text)
                print(
                    idx + 1,
                    ". made sentence: ",
                    line.text,
                    " (",
                    sentence_obj.definition,
                    ")",
                )
                sentences_with_definition.append(sentence_obj)
        return sentences_with_definition

    def _make_sentence_object(self, sentence):
        translation = translate_jp_to_en(sentence)
        sentence_obj = JapaneseSentence(sentence, translation)
        sentence_obj.audio_file_path = save_jp_text_as_audio(
            sentence_obj.sentence, is_sentence=True
        )
        sentence_obj.words = self._extract_words_for_sentence(sentence_obj)
        return sentence_obj

    def _extract_words_for_sentence(self, sentence: JapaneseSentence):
        words = self.word_extractor.extract_words_from_text(sentence.sentence)
        return words
