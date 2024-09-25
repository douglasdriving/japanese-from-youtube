from .youtube_transcriber import get_japanese_transcript_as_single_text
from .text_handling.word_extractor import extract_new_words_from_text
from .text_handling.japanese_word import JapaneseWord


def extract_words_from_transcript(japanese_transcript):
    print("Successfully retrieved Japanese transcript")
    allWords: list[JapaneseWord] = extract_new_words_from_text(japanese_transcript)
    return allWords


def extract_words_from_youtube(video_id):
    japanese_transcript = get_japanese_transcript_as_single_text(video_id)
    if japanese_transcript is not None:
        print("Successfully retrieved Japanese transcript.")
        words = extract_words_from_transcript(japanese_transcript)
        return words
    else:
        print("EXTRACT UNIQUE WORDS ERROR: Failed to retrieve Japanese transcript.")
        return None
