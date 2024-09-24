## allows the user to add all new vocab to their anki deck
from youtube_word_extractor import extract_words_from_youtube
from speech_synthesis import save_jp_text_as_audio
from anki_word_adder import add_card_to_anki_deck, open_anki_if_not_running
from audio_player import play_audio
import time

def get_valid_youtube_id_from_user():
  print("enter a youtube video id")
  video_id = ""
  while len(video_id) != 11:
    print("Invalid video id. please enter a valid youtube video id (11 characters)")
    video_id = input()
  return video_id

def save_and_play_word_audio(reading):
    audio = save_jp_text_as_audio(reading)
    play_audio(audio)
    return audio

def add_new_vocab_from_youtube_to_anki_deck():

  open_anki_if_not_running()
  video_id = get_valid_youtube_id_from_user()

  #extract unique words from the video
  print("extracting unique words from youtube video...")
  words = extract_words_from_youtube(video_id)
  if words is None:
    print("Failed to extract unique words from youtube video. exiting")
    return
  
  #for each word, check if the user knows it
  for word in words:
    
    if(word.word == None or word.reading == None or word.translation == None):
      print("skipped word since it contained non type: ")
      print(word)
      continue

    #save and play the audio
    print("")
    print("listen to the audio...")
    audio = save_and_play_word_audio(word.reading)

    #show the translation after a delay
    time.sleep(1.5)
    print("translation: " + word.translation)

    #ask the user if they know the word
    print("do you know this word? (y/n)")
    user_input = input()
    while user_input != "y" and user_input != "n":
      print("invalid input. please enter 'y' or 'n'")
      user_input = input()
    if user_input == "y":
      print("skipped word: " + word.word + " (" + word.reading + ")")
    elif user_input == "n":
      print("adding word to anki deck")
      add_card_to_anki_deck(audio, word.translation)
    else:
      print("error: invalid input")
      
    print("-------------")
  
  print("finished adding words to anki deck")