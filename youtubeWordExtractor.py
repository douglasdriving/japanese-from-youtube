from youtubeTranscriber import get_japanese_transcript
from wordExtractor import extract_words_from_sentence

def extract_unique_words_from_youtube(video_id):
   
  japanese_transcript = get_japanese_transcript(video_id)
  
  if japanese_transcript is not None:
    allWords = []
    for line in japanese_transcript:
      allWords += extract_words_from_sentence(line['text'])
    uniqueWords = list(set(allWords))
    return uniqueWords
  
  else:
    print("EXTRACT UNIQUE WORDS ERROR: Failed to retrieve Japanese transcript.")
    return None