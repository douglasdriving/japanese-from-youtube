from youtube_transcript_api import YouTubeTranscriptApi


def combine_transcript_into_single_text(transcript):
    transcript_as_single_string = ""
    for line in transcript:
        transcript_as_single_string += line["text"]
    return transcript_as_single_string


def get_japanese_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["ja"])
        return transcript
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_japanese_transcript_as_single_text(video_id):
    transcript = get_japanese_transcript(video_id)
    if transcript is not None:
        transcript_as_single_text = combine_transcript_into_single_text(transcript)
        return transcript_as_single_text
    else:
        return None
