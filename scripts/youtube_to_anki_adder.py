## allows the user to add all new vocab to their anki deck
from .youtube_word_extractor import extract_words_from_transcript
from .text_handling.speech_synthesis import save_jp_text_as_audio
from .anki.anki_word_adder import add_card_to_anki_deck, open_anki_if_not_running
from .audio.audio_player import AudioPlayer
from .database.vocabulary_connector import VocabularyConnector
import time
from .text_handling.sentence_data_extractor import SentenceDataExtractor
from .youtube_transcriber import get_japanese_transcript_as_single_text
from .text_handling.sentence import JapaneseSentence
from .text_handling.japanese_word import JapaneseWord

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


def save_sentences_and_add_unknowns_to_anki_from_transcript(transcript: str):
    sentece_data_extractor = SentenceDataExtractor(transcript)
    sentences = sentece_data_extractor.extract_sentences_not_in_db()
    for sentence in sentences:
        if sentence.is_fully_defined():
            vocabulary_connector.add_sentence(sentence)
            add_card_to_anki_deck(sentence.audio_file_path, sentence.definition)
        else:
            print("skipped sentence since it is not fully defined: ")
            print(sentence.sentence)


def add_word_to_db_and_anki_if_new(word: JapaneseWord):
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
        next_db_id = vocabulary_connector.get_highest_word_id() + 1
        audio_path = save_jp_text_as_audio(word.reading, next_db_id, is_sentence=False)
        vocabulary_connector.save_word_in_db(word, audio_path)
        add_card_to_anki_deck(audio_path, word.definition)
        print("added word: " + word.word + " (" + word.reading + ")")


def add_new_words(transcript: str):
    words = extract_words_from_transcript(transcript)
    if words is None:
        print("Failed to extract unique words from youtube video. exiting")
        return
    for word in words:
        add_word_to_db_and_anki_if_new(word)


def add_new_vocab_from_youtube_to_anki_deck():
    open_anki_if_not_running()
    video_id = get_valid_youtube_id_from_user()
    print("extracting unique words from youtube video...")
    transcript = get_japanese_transcript_as_single_text(video_id)
    add_new_words(transcript)
    save_sentences_and_add_unknowns_to_anki_from_transcript(transcript)
    print("finished adding vocab to anki deck")
