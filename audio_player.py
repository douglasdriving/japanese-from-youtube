#plays audio from a wav file
from pydub import AudioSegment
from pydub.playback import play
import os

def play_audio(audio_file):
  sound = AudioSegment.from_file(audio_file, format="wav")
  play(sound)