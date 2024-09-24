from youtube_transcript_api import YouTubeTranscriptApi

def get_japanese_transcript(video_id):
  try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja'])
    return transcript
  except Exception as e:
    print(f"Error: {e}")
    return None