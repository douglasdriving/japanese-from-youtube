from youtubeTranscriber import get_japanese_transcript
from wordExtractor import extract_japanese_words

def extract_unique_words_from_youtube(video_id):
   
  japanese_transcript = get_japanese_transcript(video_id)
  
  if japanese_transcript is not None:
    line_count = len(japanese_transcript)
    print("Successfully retrieved Japanese transcript. Lines to extract words from: " + str(line_count))
    allWords = []
    lines_extracted_from = 1
    for line in japanese_transcript:
      print("extracting line " + str(lines_extracted_from) + "...")
      allWords += extract_japanese_words(line['text'])
      print("Extracted words from line " + str(lines_extracted_from) + "/" + str(line_count) + ": " + line['text'])
      lines_extracted_from += 1
    uniqueWords = list(set(allWords))
    return uniqueWords
  else:
    print("EXTRACT UNIQUE WORDS ERROR: Failed to retrieve Japanese transcript.")
    return None