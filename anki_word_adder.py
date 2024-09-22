import requests
import os

#could move this into env vars
deck_name = 'jp_audio_cards'
anki_connect_url = 'http://localhost:8765'

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
  card = create_audio_card(deck_name, "", translation, audio_file)
  response = requests.post(anki_connect_url, json=card)
  return response.json()