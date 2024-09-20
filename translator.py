from googletrans import Translator

translator = Translator()

class WordWithTranslation:
  def __init__(self, word, translation):
    self.word = word
    self.translation = translation

def translate_word_from_jp_to_en(text):
    translation = translator.translate(text, dest='en')
    return translation.text

def translate_word_array(japanese_words):
  wordsWithTranslation = []
  for word in japanese_words:
    translation = translate_word_from_jp_to_en(word)
    wordWithTranslation = WordWithTranslation(word, translation)
    wordsWithTranslation.append(wordWithTranslation)
  return wordsWithTranslation