import requests
import os
import subprocess
import time

#could move this into env vars
deck_name = 'jp_audio_cards'
anki_connect_url = 'http://localhost:8765'
anki_path = r"C:\Users\dougl\AppData\Local\Programs\Anki\anki.exe"

def is_anki_running():
    try:
        response = requests.get("http://localhost:8765")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
      
def open_anki():
    try:
        subprocess.Popen([anki_path])
        print("Opening Anki...")
    except Exception as e:
        print(f"Failed to open Anki: {e}")
        
def open_anki_if_not_running():
    if not is_anki_running():
        open_anki()

def get_card_options(deck_name):
  options = {
    "allowDuplicate": False,
    "duplicateScope": "deck",
    "duplicateScopeOptions": {
        "deckName": deck_name,
        "checkChildren": False,
        "checkAllModels": False
    }
  },
  return options
  
def create_anki_audio(audio_file_path):
  audio_absolute_path = os.path.abspath(audio_file_path)
  audio_base_name = os.path.basename(audio_file_path)
  audio = [{
    "path": audio_absolute_path,
    "filename": audio_base_name,
    "skipHash": "7e2c2f954ef6051373ba916f000168dc",
    "fields": ["Front"]
  }]
  return audio

def create_audio_card(deck_name, front, back, audio_file_path):
  card = {
    "action": "addNote",
    "version": 6,
    "params": {
        "note": {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {
                "Front": front,
                "Back": back
            },
            "options": get_card_options(deck_name),
            "audio": create_anki_audio(audio_file_path),
        }
    }
  }
  return card

def add_card_to_anki_deck(audio_file, translation):
  open_anki_if_not_running()
  time.sleep(3) #just to make sure it gets time to open. not ideal but works for now
  card = create_audio_card(deck_name, "", translation, audio_file)
  response = requests.post(anki_connect_url, json=card)
  print(response.json())
  return response.json()

add_card_to_anki_deck("./audios/arubamy.wav", "album")