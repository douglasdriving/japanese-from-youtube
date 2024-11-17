from .word import JapaneseWord
import deepl
import os
from dotenv import load_dotenv


class Translator:

    deepl_translator: deepl.Translator

    def __init__(self):
        load_dotenv()
        self.deepl_translator = deepl.Translator(os.getenv("DEEPL_API_KEY"))

    def translate_jp_to_en(self, text: str):
        result = self.deepl_translator.translate_text(text, target_lang="EN-US")
        return result.text

    def translate_word_array(self, japanese_words):
        wordsWithTranslation = []
        for word in japanese_words:
            translation = self.translate_jp_to_en(word)
            wordWithTranslation = JapaneseWord(word, translation)
            wordsWithTranslation.append(wordWithTranslation)
        return wordsWithTranslation
