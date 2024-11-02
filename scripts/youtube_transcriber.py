from youtube_transcript_api import YouTubeTranscriptApi
from scripts.transcript_line import TranscriptLine


class YoutubeTranscriber:

    def __init__(self):
        pass

    def get_transcript(video_id):
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
