from youtubeTranscriber import get_japanese_transcript
from wordExtractor import extract_words_from_sentence
from youtubeWordExtractor import extract_unique_words_from_youtube

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
    words = extract_words_from_sentence(testSentence)
    print("tested Extracted words:")
    for word in words:
        print("word:", word)

def test_extract_words_from_youtube():
   
  print("Testing test_extract_words_from_youtube()...")
  video_id = 'eXgMsg8WouU'
  uniqueWords = extract_unique_words_from_youtube(video_id)

  if uniqueWords is not None:
    print("Successfully extracted unique words. Words:")
    for word in uniqueWords:
      print("word: ", word)

  else:
    print("FAILED TO EXTRACT UNIQUE WORDS")

test_extract_words_from_youtube()