from .japanese_word import JapaneseWord
from jisho_api.tokenize import Tokens
from jisho_api.word import Word
from ..database.word_db_connector import WordDbConnector
from .speech_synthesizer import SpeechSynthesizer
import re
import warnings


class WordExtractor:

    vocabulary_connector: WordDbConnector
    speech_synthesizer: SpeechSynthesizer

    def __init__(self):
        self.vocabulary_connector = WordDbConnector()
        self.speech_synthesizer = SpeechSynthesizer()

    def extract_words_from_text(self, text: str):
        cleaned_text = self._clean_text(text)
        word_texts = self._get_unique_words_from_text(cleaned_text)
        japanese_words = []
        if word_texts is not None:
            for word in word_texts:
                japanese_word = self._get_japanese_word(word)
                if japanese_word is not None:
                    japanese_words.append(japanese_word)
        return japanese_words

    def _get_unique_words_from_text(self, text):
        cleaned_text = self._clean_text(text)
        if self._get_japanese_word(cleaned_text) is not None:
            return [cleaned_text]
        tokens_result = Tokens.request(cleaned_text)
        if not tokens_result or not tokens_result.data:
            print(
                f"WARNING: Could not find tokens in Jisho API. Will not return any words for text: {cleaned_text}"
            )
            return None
        tokens = tokens_result.data
        clean_tokens = self._cleanup_tokens(tokens)
        words = [token.token for token in clean_tokens]
        return words

    def _clean_text(self, text: str):
        jp_text = re.sub(r"[a-zA-Z]", "", text)
        cleaned_jp_text = re.sub(r"[、。]", " ", jp_text)
        return cleaned_jp_text

    def _cleanup_tokens(self, tokens):

        def cleanup_word(word):
            word = word.replace(".", "")
            word = word.replace("。", "")
            word = word.replace("、", "")
            word = word.replace(".", "")
            return word

        def contains_latin_characters(text: str) -> bool:
            return any("a" <= char <= "z" or "A" <= char <= "Z" for char in text)

        cleaned_up_list = []

        for token in tokens:

            is_valid = not token.pos_tag.name == "unk"
            is_japanese = not contains_latin_characters(token.token)
            is_duplicate = False
            for saved_token in cleaned_up_list:
                if token.token == saved_token.token:
                    is_duplicate = True
                    break

            if not is_duplicate and is_valid and is_japanese:
                token.token = cleanup_word(token.token)
                cleaned_up_list.append(token)

        return cleaned_up_list

    def _get_japanese_word(self, kana_word: str):
        japanese_word = self.vocabulary_connector.get_word_if_exists(kana_word)
        if japanese_word == None:
            japanese_word = self._make_new_japanese_word(kana_word)
        return japanese_word

    def _make_new_japanese_word(self, kana_word: str):

        def get_definitions_as_string(senses):
            definitions = senses[0].english_definitions[:3]
            return "; ".join(definitions)

        base_word_result = None
        try:
            base_word_result = Word.request(kana_word)
        except Exception as e:
            print(f"Error when trying to get word ({kana_word}) from Jisho API: {e}")
            return None

        if not base_word_result or not base_word_result.data:
            return None

        base_word_data = base_word_result.data[0]
        japanese_info = base_word_data.japanese[0]
        base_word = japanese_info.word or japanese_info.reading
        definitions_as_string = get_definitions_as_string(base_word_data.senses)
        audio_file_path = self.speech_synthesizer.save_jp_text_as_audio(
            base_word, is_sentence=False
        )

        japanese_word = JapaneseWord(
            base_word, japanese_info.reading, definitions_as_string, audio_file_path
        )
        return japanese_word
