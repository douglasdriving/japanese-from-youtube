# extracts sentence data from a given japanese text
from .sentence import JapaneseSentence
from .speech_synthesis import save_jp_text_as_audio
from ..database.vocabulary_connector import VocabularyConnector
from .translator import translate_jp_to_en
from .word_extractor_new import WordExtractor


class SentenceDataExtractor:

    kana_text: str
    sentences: list[JapaneseSentence]
    vocabulary_connector: VocabularyConnector
    word_extractor: WordExtractor

    def __init__(self, kana_text: str = None):
        self.kana_text: str = kana_text
        self.sentences: list[JapaneseSentence] = []
        self.vocabulary_connector = VocabularyConnector()
        self.word_extractor = WordExtractor()

    def extract_sentences_not_in_db(self):
        print("Extracting sentences...")
        if self.kana_text is None:
            print("ERROR: No text to extract sentences from")
            return None
        self.remove_latin_characters()
        all_sentences_in_text_str = self._split_text_into_sentences()
        new_sentences_str = self._get_sentences_from_list_that_are_not_in_db(
            all_sentences_in_text_str
        )
        print("Found ", len(new_sentences_str), " new sentences")
        sentences_with_data: list[JapaneseSentence] = (
            self._make_new_sentences_into_objects(new_sentences_str)
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
        self.kana_text = "".join([char for char in self.kana_text if ord(char) >= 128])

    def _turn_string_list_into_sentence_list(self, sentences_str: list[str]):
        sentences: list[JapaneseSentence] = []
        for sentence in sentences_str:
            sentences.append(JapaneseSentence(sentence))
        return sentences

    def _split_text_into_sentences(self):
        sentences = self.kana_text.split("。")
        sentences = [sentence for sentence in sentences if sentence != ""]
        return sentences

    def _get_sentences_from_list_that_are_not_in_db(self, sentences: list[str]):
        sentences = [
            sentence
            for sentence in sentences
            if not self.vocabulary_connector.check_if_sentence_exists(sentence)
        ]
        return sentences

    def _make_new_sentences_into_objects(self, kana_sentences: list[str]):
        print("making ", len(kana_sentences), " sentences")
        sentences_with_definition: list[JapaneseSentence] = []
        for idx, sentence in enumerate(kana_sentences):
            sentence_exists = self.vocabulary_connector.check_if_sentence_exists(
                sentence
            )
            if sentence_exists:
                print(
                    idx + 1,
                    ". skipping sentence since it already exists: ",
                    sentence,
                )
            else:
                sentence_obj = self._make_sentence_object(sentence)
                print(
                    idx + 1,
                    ". made sentence: ",
                    sentence,
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
