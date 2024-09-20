from youtubeTranscriber import get_japanese_transcript
from wordExtractor import extract_words_from_sentence
from youtubeWordExtractor import extract_unique_words_from_youtube
from translator import translate_word_array

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

def test_word_array_translator():
  print("Testing translate_word_array()...")
  arrayOfJapaneseWords = ["今日", "部屋", "そうじ", "しました"]
  translatedWords = translate_word_array(arrayOfJapaneseWords)
  print("Translated words:")
  for word in translatedWords:
    print(" - " + word.word + " " + word.translation)

def test_extract_translated_words_from_youtube():

  print("Testing test_extract_translated_words_from_youtube()...")
  video_id = 'eXgMsg8WouU'
  words = extract_unique_words_from_youtube(video_id)
  if words is not None:
    print("successfully extracted unique words. Translating...")
    translatedWords = translate_word_array(words)
    if translatedWords is not None:
      print("successfully extracted translated words:")
      for word in translatedWords:
        print(" - " + word.word + " " + word.translation)
    else:
      print("FAILED TO TRANSLATE WORDS")
  else:
    print("FAILED TO EXTRACT UNIQUE WORDS")

test_extract_translated_words_from_youtube()