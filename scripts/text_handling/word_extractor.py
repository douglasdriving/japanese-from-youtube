# import subprocess
import re
from jisho_api.tokenize import Tokens
from jisho_api.word import Word
from .japanese_word import JapaneseWord
from ..database.vocabulary_connector import VocabularyConnector


def cleanup_word(word):
    word = word.replace(".", "")
    word = word.replace("。", "")
    word = word.replace("、", "")
    word = word.replace(".", "")
    return word


def get_word_data(kana_word: str):

    def get_definitions_as_string(base_word_data):
        definitions_of_most_common_reading = base_word_data.senses[
            0
        ].english_definitions
        definitions_limited_to_3 = definitions_of_most_common_reading[:3]
        definitions_as_string = "; ".join(definitions_limited_to_3)
        return definitions_as_string

    base_word_result = Word.request(kana_word)
    if base_word_result == None:
        return None

    base_word_data = base_word_result.data[0]
    base_word = base_word_data.japanese[0].word
    most_common_reading = base_word_data.japanese[0].reading

    if base_word == None:
        base_word = most_common_reading

    definitions_as_string = get_definitions_as_string(base_word_data)
    japanese_word = JapaneseWord(base_word, most_common_reading, definitions_as_string)
    return japanese_word


def contains_latin_characters(text: str) -> bool:
    return any("a" <= char <= "z" or "A" <= char <= "Z" for char in text)


def cleanup_tokens(list_of_tokens):

    cleaned_up_list = []

    for token in list_of_tokens:

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


def get_tokens_from_text(text):
    cleaned_text = re.sub(r"[、。]", " ", text)
    tokens_result = Tokens.request(cleaned_text)
    tokens = tokens_result.data
    clean_tokens = cleanup_tokens(tokens)
    return clean_tokens


def extract_new_words_from_text(text):
    vocabulary_connector = VocabularyConnector()
    japanese_words: list[JapaneseWord] = []
    tokens = get_tokens_from_text(text)
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
