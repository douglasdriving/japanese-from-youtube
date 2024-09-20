from youtubeTranscriber import get_japanese_transcript
from wordExtractor import extract_words_from_japanese_sentence

def test_get_japanese_transcript():

  print("Testing get_japanese_transcript()...")
  video_id = 'eXgMsg8WouU'
  japanese_transcript = get_japanese_transcript(video_id)

  if japanese_transcript is not None:
    print("Successfully retrieved Japanese transcript.")
    print("number of lines: " + str(len(japanese_transcript)))

  else:
    print("Failed to retrieve Japanese transcript.")

def test_extractWordsFromTranscript():
    print("Testing extractWordsFromTranscript()...")
    testSentence = "今日は、部屋のそうじをしました。"
    words = extract_words_from_japanese_sentence(testSentence)
    print("Extracted words:")
    for word in words:
        print("word:", word)

#problem now: the words are over-segmented, meaning that word components are split.
#e.g. 'しました' is split into 'し' and 'まし' and 'た'
#solution(s): (1) use a different dictionary for mecab, (2) use a different tokenizer, (3) use a different api or lib to extract words


# test_get_japanese_transcript()
test_extractWordsFromTranscript()