class JapaneseWord:
  
  def __init__(self, word, reading, translation):
    self.word = word
    self.reading = reading
    self.translation = translation
  
  def is_same(self, other):
    is_same_word = self.word == other.word
    is_same_reading = self.reading == other.reading
    is_same_translation = self.translation == other.translation
    is_exact_same_word = is_same_word and is_same_reading and is_same_translation
    return is_exact_same_word

  def is_fully_defined(self):
    return self.word != None and self.reading != None and self.translation != None