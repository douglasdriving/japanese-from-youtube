## allows the user to add all new vocab to their anki deck
from .youtube_word_extractor import extract_words_from_youtube
from .text_handling.speech_synthesis import save_jp_text_as_audio
from .anki.anki_word_adder import add_card_to_anki_deck, open_anki_if_not_running
from .audio.audio_player import AudioPlayer
from .database.vocabulary_connector import VocabularyConnector
import time

audioPlayer = AudioPlayer("")


def get_valid_youtube_id_from_user():
    print("enter a youtube video id")
    video_id = ""
    while len(video_id) != 11:
        print("Invalid video id. please enter a valid youtube video id (11 characters)")
        video_id = input()
    return video_id


def save_and_play_word_audio(reading):
    audio = save_jp_text_as_audio(reading)
    audioPlayer.play_audio_file(audio)
    return audio


def add_new_vocab_from_youtube_to_anki_deck():

    open_anki_if_not_running()
    video_id = get_valid_youtube_id_from_user()

    # extract unique words from the video
    print("extracting unique words from youtube video...")
    words = extract_words_from_youtube(video_id)
    if words is None:
        print("Failed to extract unique words from youtube video. exiting")
        return

    vocabulary_connector = VocabularyConnector()

    # for each word, check if the user knows it
    for word in words:

        if not word.is_fully_defined():
            print("skipped word since it is not fully defined: ")
            print(word)
            continue

        if vocabulary_connector.check_if_word_exists(
            word.word
        ):  # but, we should also do this earlier...
            print("skipped word since it already exists in the database: ")
            print(word.word, "(", word.reading, ")")
            continue

        # save and play the audio
        print("")
        print("listen to the audio...")
        audio = save_and_play_word_audio(word.reading)

        # save word in db
        try:
            vocabulary_connector.add_word(word, audio)
        except Exception as e:
            print("error adding word to database. error: ", e, " word: ", word)
            continue

        # show the translation after a delay
        time.sleep(1.5)
        print("translation: " + word.definition)

        # ask the user if they know the word
        print("do you know this word? (y/n)")
        user_input = input()
        while user_input != "y" and user_input != "n":
            print("invalid input. please enter 'y' or 'n'")
            user_input = input()
        if user_input == "y":
            print("skipped word: " + word.word + " (" + word.reading + ")")
        elif user_input == "n":
            print("adding word to anki deck")
            add_card_to_anki_deck(audio, word.definition)
        else:
            print("error: invalid input")

        print("-------------")

    print("finished adding words to anki deck")
