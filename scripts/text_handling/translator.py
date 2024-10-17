from .japanese_word import JapaneseWord
import deepl
import os
from dotenv import load_dotenv

load_dotenv()
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
translator = deepl.Translator(DEEPL_API_KEY)


def translate_jp_to_en(text: str):
    result = translator.translate_text(text, target_lang="EN-US")
    return result.text


def translate_word_array(japanese_words):
    wordsWithTranslation = []
    for word in japanese_words:
        translation = translate_jp_to_en(word)
        wordWithTranslation = JapaneseWord(word, translation)
        wordsWithTranslation.append(wordWithTranslation)
    return wordsWithTranslation
