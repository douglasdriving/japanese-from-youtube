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


def save_and_play_word_audio(reading):
    audio = save_jp_text_as_audio(reading)
    audioPlayer.play_audio_file(audio)
    return audio


def save_sentence_to_anki_if_user_doesnt_know(sentence: JapaneseSentence):
    print("playing audio for sentence...")
    audioPlayer.play_audio_file(sentence.audio_file_path)
    user_knows_sentence = get_yes_or_no_input_from_user(
        "do you know the meaning of this sentence sentence? (y/n)"
    )
    if not user_knows_sentence:
        print("adding sentence to anki deck")
        add_card_to_anki_deck(sentence.audio_file_path, sentence.definition)


def save_sentences_and_add_unknowns_to_anki_from_transcript(transcript: str):
    sentece_data_extractor = SentenceDataExtractor(transcript)
    sentences = sentece_data_extractor.extract_sentences_not_in_db()
    for sentence in sentences:
        if sentence.is_fully_defined():
            vocabulary_connector.add_sentence(sentence)
            save_sentence_to_anki_if_user_doesnt_know(sentence)
        else:
            print("skipped sentence since it is not fully defined: ")
            print(sentence.sentence)


def add_word_from_transcript_to_db_and_anki_if_user_says_its_new(word: JapaneseWord):
    if not word.is_fully_defined():
        print(
            "skipped word since it is not fully defined: ",
            word.word,
            ", ",
            word.definition,
        )
        return

    if vocabulary_connector.check_if_word_exists(
        word.word
    ):  # but, we should also do this earlier...
        print("skipped word since it already exists in the database: ")
        print(word.word, "(", word.reading, ")")
        return

    # save and play the audio
    print("")
    print("listen to the audio...")
    audio = save_and_play_word_audio(word.reading)

    # save word in db
    try:
        vocabulary_connector.add_word(word, audio)
    except Exception as e:
        print("error adding word to database. error: ", e, " word: ", word)
        return

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


def add_new_words(transcript: str):
    words = extract_words_from_transcript(transcript)
    if words is None:
        print("Failed to extract unique words from youtube video. exiting")
        return
    for word in words:
        add_word_from_transcript_to_db_and_anki_if_user_says_its_new(word)


def add_new_vocab_from_youtube_to_anki_deck():
    open_anki_if_not_running()
    video_id = get_valid_youtube_id_from_user()
    print("extracting unique words from youtube video...")
    transcript = get_japanese_transcript_as_single_text(video_id)
    add_new_words(transcript)
    save_sentences_and_add_unknowns_to_anki_from_transcript(transcript)
    print("finished adding vocab to anki deck")
