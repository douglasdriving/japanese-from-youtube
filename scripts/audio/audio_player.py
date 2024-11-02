from pydub import AudioSegment
from pydub.playback import play


class AudioPlayer:
    def __init__(self, audio_file=""):
        self.audio_file = audio_file
        self.sound = None

    def load_audio(self):
        self.sound = AudioSegment.from_file(self.audio_file, format="wav")

    def set_audio_file(self, audio_file):
        self.audio_file = audio_file
        self.sound = None

    def play_audio(self):
        if self.sound is None:
            self.load_audio()
        play(self.sound)

    def play_audio_file(self, audio_file):
        self.set_audio_file(audio_file)
        self.play_audio()
