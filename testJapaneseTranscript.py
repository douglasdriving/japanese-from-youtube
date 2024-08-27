from youtubeTranscriber import get_japanese_transcript

def test_get_japanese_transcript():
  print("Testing get_japanese_transcript()...")
  video_id = 'eXgMsg8WouU'
  japanese_transcript = get_japanese_transcript(video_id)
  if japanese_transcript is not None:
    print("Successfully retrieved Japanese transcript.")
    print("number of lines: " + str(len(japanese_transcript)))
    print("transcript lin by line:")
    for e in japanese_transcript:
      print(e)
  else:
    print("Failed to retrieve Japanese transcript.")

test_get_japanese_transcript()