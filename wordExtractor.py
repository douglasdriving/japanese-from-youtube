# import subprocess
# import re
from jisho_api.tokenize import Tokens
from jisho_api.word import Word
from japanese_word import JapaneseWord

def extract_japanese_words(sentence):
  
  japanese_words = []
  tokens_result = Tokens.request(sentence)
  
  if(tokens_result == None):
    print("Failed to extract tokens from sentence: " + sentence)
    return japanese_words
  
  tokens = tokens_result.data
  
  for token in tokens:
    if(token.pos_tag.name == "unk"):
      continue
    
    word_in_sentence = token.token
    
    word_in_sentence.replace('.', '')
    word_in_sentence.replace('。', '')
    word_in_sentence.replace('、', '')
    word_in_sentence.replace('.', '')
    
    base_word_result = Word.request(word_in_sentence)
    if(base_word_result == None):
      continue
    base_word_data = base_word_result.data[0]
    base_word = base_word_data.japanese[0].word
    most_common_reading = base_word_data.japanese[0].reading
    if(base_word == None):
      base_word = most_common_reading
    definitions_of_most_common_reading = base_word_data.senses[0].english_definitions
    definitions_as_string = '; '.join(definitions_of_most_common_reading)
    japanese_word = JapaneseWord(base_word, most_common_reading, definitions_as_string)
    japanese_words.append(japanese_word)
    
  return japanese_words
  
# #test
# sentence = "私は日本語を勉強しています。smaljj"
# extracted_words = extract_japanese_words(sentence)
# for word in extracted_words:
#   print(word.word, word.reading, word.translation)


# def extract_words_from_sentence(sentence):
#   ichiranCommand = '(ichiran/dict:simple-segment "' + sentence + '")'
#   cliCommand = ['ichiran-cli', '-e', ichiranCommand]
#   result = subprocess.run(cliCommand, capture_output=True, text=True, encoding='utf-8')
#   output_string = result.stdout
#   # Use regex to find all kanji characters
#   kanji_matches = re.findall(r'\w+\[', output_string)
#   # Extract the kanji (remove the brackets)
#   kanji_words = [match[:-1] for match in kanji_matches]
#   # Filter out empty strings (if any)
#   kanji_words = [word for word in kanji_words if word]
#   return kanji_words