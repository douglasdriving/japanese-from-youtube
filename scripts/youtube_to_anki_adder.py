## allows the user to add all new vocab to their anki deck
from .youtube_word_extractor import extract_new_words_from_transcript
from .text_handling.speech_synthesis import save_jp_text_as_audio
from .anki.anki_word_adder import (
    add_words_and_sentences_to_anki,
    open_anki_if_not_running,
)
from .audio.audio_player import AudioPlayer
from .database.vocabulary_connector import VocabularyConnector
import time
from .text_handling.sentence_data_extractor import SentenceDataExtractor
from .youtube_transcriber import get_transcript
from .text_handling.sentence import JapaneseSentence
from .text_handling.japanese_word import JapaneseWord
from .anki.anki_note import AnkiNote

audioPlayer = AudioPlayer("")
vocabulary_connector = VocabularyConnector()


def get_yes_or_no_input_from_user(prompt: str):
    print(prompt)
    user_input = input()
    while user_input != "y" and user_input != "n":
        print("invalid input. please enter 'y' or 'n'")
        user_input = input()
    if user_input == "y":
        return True
    else:
        return False


def get_valid_youtube_id_from_user():
    print("enter a youtube video id")
    video_id = ""
    while len(video_id) != 11:
        print("Invalid video id. please enter a valid youtube video id (11 characters)")
        video_id = input()
    return video_id


def add_sentence_to_db(sentence: JapaneseSentence):
    if sentence.is_fully_defined():
        vocabulary_connector.add_sentence(sentence)
    else:
        print("skipped adding sentence to db since it is not fully defined: ")
        print(sentence.sentence)


def add_word_to_db_if_new(word: JapaneseWord):
    if not word.is_fully_defined():
        print(
            "skipped word since it is not fully defined: ",
            word.word,
            ", ",
            word.definition,
        )
    elif vocabulary_connector.check_if_word_exists(word.word):
        print(
            "skipped word since it already exists in the database: ",
            word.word,
            "(",
            word.reading,
            ")",
        )
    else:
        vocabulary_connector.save_word_in_db(word)
        print("added word to db: " + word.word + " (" + word.reading + ")")


def add_new_words_to_db(transcript: str):
    words = extract_new_words_from_transcript(transcript)
    words_added: list[JapaneseWord] = []
    if words is None:
        print("Failed to extract unique words from youtube video. exiting")
        return
    for word in words:
        word = add_word_to_db_if_new(word)
        if type(word) is JapaneseWord:
            words_added.append(word)
    return words_added


def add_words_and_sentences_to_db(sentences: list[JapaneseSentence]):
    for sentence in sentences:
        for word in sentence.words:
            add_word_to_db_if_new(word)
        add_sentence_to_db(sentence)


def add_new_vocab_from_youtube_to_anki_deck():
    open_anki_if_not_running()
    video_id = get_valid_youtube_id_from_user()
    print("extracting sentences and words from youtube video...")
    transcript = get_transcript(video_id)
    sentence_data_extractor = SentenceDataExtractor(transcript)
    sentences = sentence_data_extractor.extract_sentences_not_in_db()
    add_words_and_sentences_to_db(sentences)
    add_words_and_sentences_to_anki(sentences)
    print("finished adding vocab to anki deck")
