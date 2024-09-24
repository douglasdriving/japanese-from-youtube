from youtubeTranscriber import get_japanese_transcript
from word_extractor import extract_words_from_sentence
from youtube_word_extractor import extract_words_from_youtube
from translator import translate_word_array
from speech_synthesis import save_jp_text_as_audio
import time

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
  uniqueWords = extract_words_from_youtube(video_id)

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
  words = extract_words_from_youtube(video_id)
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

def test_save_vocab_audio_from_youtube_video():
  print("Testing save_audio_from_youtube_video()...")
  video_id = 'eXgMsg8WouU'
  words = extract_words_from_youtube(video_id)

  if words is not None:

    print("successfully extracted unique words. Translating...")

    #translate the words
    translatedWords = translate_word_array(words)
    if translatedWords is not None:
      print("successfully extracted translated words:")
      for word in translatedWords:
        print(" - " + word.word + " " + word.translation)
    else:
      print("FAILED TO TRANSLATE WORDS")
    
    #save words as audio files
    print("saving audio files...")
    for word in words:
      audio_file = save_jp_text_as_audio(word)
      print(" - audio file saved: " + audio_file)

  else:
    print("FAILED TO EXTRACT UNIQUE WORDS")

test_save_vocab_audio_from_youtube_video()