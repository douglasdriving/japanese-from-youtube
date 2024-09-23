# import subprocess
# import re
from jisho_api.tokenize import Tokens
from jisho_api.word import Word
from japanese_word import JapaneseWord

def get_tokens_from_text(text):
  tokens_result = Tokens.request(text)
  if(tokens_result == None):
    print("Failed to extract tokens from text: " + text)
    return None
  tokens = tokens_result.data
  return tokens

def cleanup_word(word):
  word = word.replace('.', '')
  word = word.replace('。', '')
  word = word.replace('、', '')
  word = word.replace('.', '')
  return word

def get_word_from_token(token):
    if(token.pos_tag.name == "unk"):
      return None
    
    word_in_sentence = token.token
    word_in_sentence = cleanup_word(word_in_sentence)
    
    base_word_result = Word.request(word_in_sentence)
    if(base_word_result == None):
      return None
    
    base_word_data = base_word_result.data[0]
    base_word = base_word_data.japanese[0].word
    most_common_reading = base_word_data.japanese[0].reading
    
    if(base_word == None):
      base_word = most_common_reading
      
    definitions_of_most_common_reading = base_word_data.senses[0].english_definitions
    definitions_as_string = '; '.join(definitions_of_most_common_reading)
    japanese_word = JapaneseWord(base_word, most_common_reading, definitions_as_string)
    return japanese_word

def extract_japanese_words(sentence):
  japanese_words = []
  tokens = get_tokens_from_text(sentence)
  if(tokens != None):
    for token in tokens:
      japanese_word = get_word_from_token(token)
      if(japanese_word != None):
        japanese_words.append(japanese_word)
  return japanese_words


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