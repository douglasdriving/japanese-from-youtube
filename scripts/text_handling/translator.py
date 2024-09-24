from googletrans import Translator
from .japanese_word import JapaneseWord

translator = Translator()

def translate_word_from_jp_to_en(text):
    translation = translator.translate(text, dest='en')
    return translation.text

def translate_word_array(japanese_words):
  wordsWithTranslation = []
  for word in japanese_words:
    translation = translate_word_from_jp_to_en(word)
    wordWithTranslation = JapaneseWord(word, translation)
    wordsWithTranslation.append(wordWithTranslation)
  return wordsWithTranslation