from youtube_transcript_api import YouTubeTranscriptApi
from scripts.text_handling.transcript_line import TranscriptLine
import requests


class YoutubeTranscriber:

    def __init__(self):
        pass

    def transcribe(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["ja"])
            transcript_lines = [
                TranscriptLine(line["text"], line["start"], line["duration"])
                for line in transcript
            ]
            return transcript_lines
        except Exception as e:
            print(f"Failed to get transcript. Error: {e}")
            return None

    def get_video_title(self, youtube_video_id):
        try:
            url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={youtube_video_id}&format=json"
            response = requests.get(url)
            data = response.json()
            return data["title"]
        except Exception as e:
            print(f"Failed to get video title. Error: {e}")
            return None
