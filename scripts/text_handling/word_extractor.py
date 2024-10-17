# import subprocess
# import re
from jisho_api.tokenize import Tokens
from jisho_api.word import Word
from .japanese_word import JapaneseWord
from ..database.vocabulary_connector import VocabularyConnector


def get_tokens_from_text(text):
    tokens_result = Tokens.request(text)
    if tokens_result == None:
        print("Failed to extract tokens from text: " + text)
        return None
    tokens = tokens_result.data
    return tokens


def cleanup_word(word):
    word = word.replace(".", "")
    word = word.replace("。", "")
    word = word.replace("、", "")
    word = word.replace(".", "")
    return word


def get_word_data(kana_word: str):

    base_word_result = Word.request(kana_word)
    if base_word_result == None:
        return None

    base_word_data = base_word_result.data[0]
    base_word = base_word_data.japanese[0].word
    most_common_reading = base_word_data.japanese[0].reading

    if base_word == None:
        base_word = most_common_reading

    definitions_of_most_common_reading = base_word_data.senses[0].english_definitions
    definitions_as_string = "; ".join(definitions_of_most_common_reading)
    japanese_word = JapaneseWord(base_word, most_common_reading, definitions_as_string)
    return japanese_word


def cleanup_tokens(list_of_tokens):

    cleaned_up_list = []

    for token in list_of_tokens:

        is_duplicate = False
        is_valid = True

        for saved_token in cleaned_up_list:
            if token.token == saved_token.token:
                is_duplicate = True
                break

        if token.pos_tag.name == "unk":
            is_valid = False

        if not is_duplicate and is_valid:
            token.token = cleanup_word(token.token)
            cleaned_up_list.append(token)

    return cleaned_up_list


def extract_new_words_from_text(text):
    vocabulary_connector = VocabularyConnector()
    japanese_words: list[JapaneseWord] = []
    tokens = get_tokens_from_text(text)
    tokens = cleanup_tokens(tokens)
    print("Extracted " + str(len(tokens)) + " tokens from text.")
    words_checked = 0
    if tokens != None:
        for token in tokens:
            words_checked += 1
            word: JapaneseWord = get_word_data(token.token)
            if word == None:
                print(str(words_checked) + ". Failed to extract word: " + token.token)
                continue
            word_already_in_db = vocabulary_connector.check_if_word_exists(word.word)
            word_in_kana = word.word
            if word_already_in_db:
                print(
                    str(words_checked) + ". Word already in database: " + word_in_kana
                )
                continue
            if word == None:
                print(str(words_checked) + ". Failed to extract word: " + word_in_kana)
                continue
            japanese_words.append(word)
            print(str(words_checked) + ". Extracted word : " + word_in_kana)
    return japanese_words
