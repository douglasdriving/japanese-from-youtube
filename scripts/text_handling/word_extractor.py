# import subprocess
# import re
from jisho_api.tokenize import Tokens
from jisho_api.word import Word
from .japanese_word import JapaneseWord

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
    # if(token.pos_tag.name == "unk"):
    #   return None
    
    word_in_sentence = token.token
    # word_in_sentence = cleanup_word(word_in_sentence)
    
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

def cleanup_tokens(list_of_tokens):
    
  cleaned_up_list = []
  
  for token in list_of_tokens:
    
    is_duplicate = False
    is_valid = True
    
    for saved_token in cleaned_up_list:
      if(token.token == saved_token.token):
        is_duplicate = True
        break
      
    if(token.pos_tag.name == "unk"):
        is_valid = False
      
    if(not is_duplicate and is_valid):
      token.token = cleanup_word(token.token)
      cleaned_up_list.append(token)
    
  return cleaned_up_list

def extract_japanese_words(text):
  japanese_words: list[JapaneseWord] = []
  tokens = get_tokens_from_text(text)
  tokens = cleanup_tokens(tokens)
  print("Extracted " + str(len(tokens)) + " tokens from text.")
  words_extracted = 0
  if(tokens != None):
    for token in tokens:
      japanese_word = get_word_from_token(token) #would it be possible to make a single call instead?
      if(japanese_word != None):
        japanese_words.append(japanese_word)
        words_extracted += 1
        print("Extracted word " + str(words_extracted) + ": " + japanese_word.word)
  return japanese_words
