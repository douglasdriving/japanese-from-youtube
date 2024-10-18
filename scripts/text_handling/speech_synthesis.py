import os
import azure.cognitiveservices.speech as speechsdk
import random
import re
from .romaziner import romanize_with_underscore

# Ensure the directory exists
os.makedirs("./audios", exist_ok=True)

speech_key = os.environ.get("SPEECH_KEY")
speech_region = os.environ.get("SPEECH_REGION")
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)


def get_random_japanese_voice_name():
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


def save_jp_text_as_audio(kana_text: str, database_id: int, is_sentence: bool):

    def create_and_save_new_audio(kana_text, audio_file_path):
        speech_config.speech_synthesis_voice_name = get_random_japanese_voice_name()
        audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file_path)
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config
        )
        speech_synthesis_result = speech_synthesizer.speak_text_async(kana_text).get()
        if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")

    audio_file_path = f"./audios/w{database_id}.wav"
    if is_sentence:
        audio_file_path = f"./audios/s{database_id}.wav"
    if not os.path.exists(audio_file_path):
        create_and_save_new_audio(kana_text, audio_file_path)
    return audio_file_path
