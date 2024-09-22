import os
import azure.cognitiveservices.speech as speechsdk
import random
from romaziner import romanize_with_underscore

speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))

def get_random_japanese_voice_name():
  japanese_voice_names = [
    "ja-JP-NanamiNeural",
    "ja-JP-KeitaNeural",
    "ja-JP-AoiNeural",
    "ja-JP-DaichiNeural",
    "ja-JP-MayuNeural",
    "ja-JP-NaokiNeural",
    "ja-JP-ShioriNeural"
  ]
  random_voice_index = random.randint(0, len(japanese_voice_names) - 1)
  return japanese_voice_names[random_voice_index]

def save_jp_text_as_audio(kana_text):

  romanized_text = romanize_with_underscore(kana_text)
  file_name = "./audios/" + romanized_text + ".wav"

  if not os.path.exists(file_name):
    speech_config.speech_synthesis_voice_name=get_random_japanese_voice_name()
    audio_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    speech_synthesis_result = speech_synthesizer.speak_text_async(kana_text).get()
    
  return file_name