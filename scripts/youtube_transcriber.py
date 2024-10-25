from youtube_transcript_api import YouTubeTranscriptApi


def remove_parenthesis_and_text_inside_it(text):
    while "(" in text:
        start = text.index("(")
        end = text.index(")")
        text = text[:start] + text[end + 1 :]
    return text


def combine_transcript_into_single_text(transcript):
    transcript_as_single_string = ""
    for line in transcript:
        line_without_readings = remove_parenthesis_and_text_inside_it(line["text"])
        transcript_as_single_string += line_without_readings
    return transcript_as_single_string


def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["ja"])
        transcript_as_single_text = combine_transcript_into_single_text(transcript)
        return transcript_as_single_text
    except Exception as e:
        print(f"Failed to get transcript. Error: {e}")
        return None
