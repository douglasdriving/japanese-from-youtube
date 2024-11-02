import os
import azure.cognitiveservices.speech as speechsdk
import random
import re


class SpeechSynthesizer:

    speech_key: str
    speech_region: str
    speech_config: speechsdk.SpeechConfig

    def __init__(self):
        os.makedirs("./audios", exist_ok=True)
        self.speech_key = os.environ.get("SPEECH_KEY")
        self.speech_region = os.environ.get("SPEECH_REGION")
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key, region=self.speech_region
        )

    def save_jp_text_as_audio(self, kana_text: str, is_sentence: bool):
        highest_id = self._get_highest_audio_id(is_sentence)
        audio_file_path = f"./audios/w{highest_id+1}.wav"
        if is_sentence:
            audio_file_path = f"./audios/s{highest_id+1}.wav"
        if not os.path.exists(audio_file_path):
            self._create_and_save_new_audio(kana_text, audio_file_path)
        return audio_file_path

    def _get_highest_audio_id(self, is_sentence: bool):
        if is_sentence:
            return self._get_highest_sentence_audio_id()
        else:
            return self._get_highest_word_audio_id()

    def _get_highest_word_audio_id(self):
        highest_id = 0
        for filename in os.listdir("./audios"):
            if filename.endswith(".wav") and os.path.basename(filename).startswith("w"):
                id = int(re.search(r"\d+", filename).group())
                if id > highest_id:
                    highest_id = id
        return highest_id

    def _get_highest_sentence_audio_id(self):
        highest_id = 0
        for filename in os.listdir("./audios"):
            if filename.endswith(".wav") and os.path.basename(filename).startswith("s"):
                id = int(re.search(r"\d+", filename).group())
                if id > highest_id:
                    highest_id = id
        return highest_id

    def _create_and_save_new_audio(self, kana_text, audio_file_path):
        self.speech_config.speech_synthesis_voice_name = (
            self._get_random_japanese_voice_name()
        )
        audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file_path)
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=audio_config
        )
        speech_synthesis_result = speech_synthesizer.speak_text_async(kana_text).get()
        if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")

    def _get_random_japanese_voice_name(self):
        japanese_voice_names = [
            "ja-JP-NanamiNeural",
            "ja-JP-KeitaNeural",
            "ja-JP-AoiNeural",
            "ja-JP-DaichiNeural",
            "ja-JP-MayuNeural",
            "ja-JP-NaokiNeural",
            "ja-JP-ShioriNeural",
        ]
        random_voice_index = random.randint(0, len(japanese_voice_names) - 1)
        return japanese_voice_names[random_voice_index]
