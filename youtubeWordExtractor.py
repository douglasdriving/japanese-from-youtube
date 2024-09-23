from youtubeTranscriber import get_japanese_transcript
from wordExtractor import extract_japanese_words

def extract_unique_words_from_youtube(video_id):
   
  japanese_transcript = get_japanese_transcript(video_id)
  
  if japanese_transcript is not None:
    print("Successfully retrieved Japanese transcript.")
    allWords = []
    for line in japanese_transcript:
      allWords += extract_japanese_words(line['text'])
      print("Extracted words from line: " + line['text'])
    uniqueWords = list(set(allWords))
    return uniqueWords
  else:
    print("EXTRACT UNIQUE WORDS ERROR: Failed to retrieve Japanese transcript.")
    return None