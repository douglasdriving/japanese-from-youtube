from .youtube_transcriber import get_japanese_transcript
from .text_handling.word_extractor import extract_new_words_from_text
from .text_handling.japanese_word import JapaneseWord


def combine_transcript_into_single_text(transcript):
    transcript_as_single_string = ""
    for line in transcript:
        transcript_as_single_string += line["text"]
    return transcript_as_single_string


def extract_words_from_transcript(japanese_transcript):
    print("Successfully retrieved Japanese transcript")
    transcript_as_single_string = combine_transcript_into_single_text(
        japanese_transcript
    )
    allWords: list[JapaneseWord] = extract_new_words_from_text(
        transcript_as_single_string
    )
    return allWords


def extract_words_from_youtube(video_id):
    japanese_transcript = get_japanese_transcript(video_id)
    if japanese_transcript is not None:
        print("Successfully retrieved Japanese transcript.")
        words = extract_words_from_transcript(japanese_transcript)
        return words
    else:
        print("EXTRACT UNIQUE WORDS ERROR: Failed to retrieve Japanese transcript.")
        return None
