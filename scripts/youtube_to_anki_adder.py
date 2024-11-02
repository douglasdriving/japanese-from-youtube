from .youtube_word_extractor import extract_new_words_from_transcript
from .anki.anki_word_adder import add_words_and_sentences_to_anki
from .audio.audio_player import AudioPlayer
from .database.vocabulary_connector import VocabularyConnector
from .text_handling.sentence_data_extractor import SentenceDataExtractor
from .youtube_transcriber import get_transcript
from .text_handling.sentence import JapaneseSentence
from .text_handling.japanese_word import JapaneseWord
from .transcript_line import TranscriptLine

audioPlayer = AudioPlayer("")
vocabulary_connector = VocabularyConnector()

# this has to be a class...


def _get_valid_youtube_id_from_user():
    print("enter a youtube video id")
    video_id = ""
    while len(video_id) != 11:
        print("Invalid video id. please enter a valid youtube video id (11 characters)")
        video_id = input()
    return video_id


def _add_sentence_to_db(sentence: JapaneseSentence):
    if sentence.is_fully_defined():
        added_sentence = vocabulary_connector.add_sentence(sentence)
        print(
            "added sentence to db: "
            + added_sentence.sentence
            + " ("
            + added_sentence.definition
            + ")"
        )
        return added_sentence
    else:
        print("skipped adding sentence to db since it is not fully defined: ")
        print(sentence.sentence)
        return None


def _add_word_to_db_if_new(word: JapaneseWord):
    if not word.is_fully_defined():
        print(
            "skipped word since it is not fully defined: ",
            word.word,
            ", ",
            word.definition,
        )
        return None

    if vocabulary_connector.check_if_word_exists(word.word):
        print(
            "skipped word since it already exists in the database: ",
            word.word,
            "(",
            word.definition,
            ")",
        )
        return None

    added_word = vocabulary_connector.save_word_in_db(word)
    if added_word:
        print("added word to db: " + word.word + " (" + word.definition + ")")
    else:
        print("failed to add word to db: " + word.word + " (" + word.definition + ")")
    return added_word


def _add_words_and_sentences_to_db(sentences: list[JapaneseSentence]):
    added_sentences: list[JapaneseSentence] = []
    for added_sentence in sentences:
        added_words: list[JapaneseWord] = []
        for word in added_sentence.words:
            added_word = _add_word_to_db_if_new(word)
            if added_word:
                added_words.append(added_word)
        added_sentence = _add_sentence_to_db(added_sentence)
        if added_sentence:
            added_sentence.words = added_words
            added_sentences.append(added_sentence)
    return added_sentences


def add_new_vocab_from_youtube_to_anki_deck():
    video_id = _get_valid_youtube_id_from_user()
    print("extracting sentences and words from youtube video...")
    transcript: list[TranscriptLine] = get_transcript(video_id)
    sentence_data_extractor = SentenceDataExtractor(transcript)
    sentences = sentence_data_extractor.extract_sentences_not_in_db()
    sentences_added_to_db = _add_words_and_sentences_to_db(sentences)
    add_words_and_sentences_to_anki(sentences_added_to_db)
    print("finished adding vocab to anki deck")
