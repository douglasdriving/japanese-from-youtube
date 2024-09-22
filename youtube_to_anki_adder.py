## allows the user to add all new vocab to their anki deck
from youtubeWordExtractor import extract_unique_words_from_youtube
from translator import translate_word_array
from speech_synthesis import save_jp_text_as_audio
import os
from anki_word_adder import add_card_to_anki_deck
from audio_player import play_audio
import time
from romaziner import romanize_with_spaces

def add_new_vocab_from_youtube_to_anki_deck():

  #ask for a valid youtube video id
  print("please enter a youtube video id")
  video_id = ""
  while len(video_id) != 11:
    print("Invalid video id. please enter a valid youtube video id")
    video_id = input()

  #extract unique words from the video
  print("extracting unique words from youtube video...")
  words = extract_unique_words_from_youtube(video_id)
  if words is None:
    print("Failed to extract unique words from youtube video. exiting")
    return

  #translate the words
  words_with_translations = translate_word_array(words)
  if words_with_translations is None:
    print("Failed to translate words. exiting")
    return
  
  #for each word, check if the user knows it
  for word in words_with_translations:

    #save and play the audio
    print("")
    print("listen to the audio...")
    audio = save_jp_text_as_audio(word.word)
    play_audio(audio)

    #show the translation after a delay
    time.sleep(1.5)
    print("translation: " + word.translation)

    #ask the user if they know the word
    print("do you know this word? (y/n)")
    user_input = input()
    if user_input == "y":
      print("skipped word: " + romanize_with_spaces(word.word))
      os.remove(audio)
    else:
      print("adding word to anki deck")
      result = add_card_to_anki_deck(audio, word.translation)
      if(result["error"]):
        print("ERROR: Failed to add word to anki deck with file path: " + audio)
      
    print("-------------")
  
  print("finished adding words to anki deck")