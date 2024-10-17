import os
import azure.cognitiveservices.speech as speechsdk
import random
from .romaziner import romanize_with_underscore

speech_config = speechsdk.SpeechConfig(
    subscription=os.environ.get("SPEECH_KEY"), region=os.environ.get("SPEECH_REGION")
)


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


def save_jp_text_as_audio(kana_text):

    print("saving audio for: " + kana_text)

    romanized_text = romanize_with_underscore(kana_text)
    print("romanized text: " + romanized_text)
    audio_file_path = "./audios/" + romanized_text + ".wav"
    print("audio file path: " + audio_file_path)

    if not os.path.exists(audio_file_path):
        speech_config.speech_synthesis_voice_name = get_random_japanese_voice_name()
        audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file_path)
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config
        )
        speech_synthesis_result = speech_synthesizer.speak_text_async(kana_text).get()

    return audio_file_path
