# extracts sentence data from a given japanese text
from .sentence import JapaneseSentence
from .speech_synthesis import save_jp_text_as_audio
from ..database.vocabulary_connector import VocabularyConnector
from .translator import translate_jp_to_en


class SentenceDataExtractor:
    def __init__(self, kana_text: str):
        self.kana_text: str = kana_text
        self.sentences: list[JapaneseSentence] = []
        self.vocabulary_connector = VocabularyConnector()

    def extract_sentences_not_in_db(self):
        if self.kana_text is None:
            print("ERROR: No text to extract sentences from")
            return None
        all_sentences_in_text = self._split_text_into_sentences()
        new_sentences = self._get_sentences_from_list_that_are_not_in_db(
            all_sentences_in_text
        )
        sentences_with_data: list[JapaneseSentence] = self._add_definition_to_sentence(
            new_sentences
        )
        self._save_and_link_audio_to_sentences(sentences_with_data)
        return sentences_with_data

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

    def _add_definition_to_sentence(self, kana_sentences: list[str]):
        print("adding definitions to sentences...", kana_sentences)
        sentences_with_definition: list[JapaneseSentence] = []
        for sentence in kana_sentences:
            translation = translate_jp_to_en(sentence)
            sentence_obj = JapaneseSentence(sentence, translation)
            sentences_with_definition.append(sentence_obj)
        return sentences_with_definition

    def _save_and_link_audio_to_sentences(
        self, senteces_with_data: list[JapaneseSentence]
    ):
        for sentence in senteces_with_data:
            audio_file_path = save_jp_text_as_audio(
                sentence.sentence
            )  # apparently, sentence is with pronunciation in parenthesis here
            sentence.audio_file_path = audio_file_path
