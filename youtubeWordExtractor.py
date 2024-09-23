from youtubeTranscriber import get_japanese_transcript
from wordExtractor import extract_japanese_words
from japanese_word import JapaneseWord

def extract_words_from_line_that_are_not_in_list(line, words_list: list[JapaneseWord]):
  extracted_words: list[JapaneseWord] = []
  words_in_line = extract_japanese_words(line['text'])
  for word_in_line in words_in_line:
    word_is_already_saved = False
    for word_in_list in words_list:
      if word_in_list.is_same(word_in_line):
        word_is_already_saved = True
        break
    if not word_is_already_saved and word_in_line != None and word_in_line.is_fully_defined():
      extracted_words.append(word_in_line)
  return extracted_words

def extract_words_from_transcript(japanese_transcript):
  line_count = len(japanese_transcript)
  print("Successfully retrieved Japanese transcript. Lines to extract words from: " + str(line_count))
  allWords: list[JapaneseWord] = []
  lines_extracted_from = 1
  for line in japanese_transcript:
    print("extracting line " + str(lines_extracted_from) + "...")
    allWords += extract_words_from_line_that_are_not_in_list(line, allWords)
    print("Extracted words from line " + str(lines_extracted_from) + "/" + str(line_count) + ": " + line['text'])
    lines_extracted_from += 1
  return allWords

def extract_words_from_youtube(video_id):
  japanese_transcript = get_japanese_transcript(video_id)
  if japanese_transcript is not None:
    print("Successfully retrieved Japanese transcript.")
    words = extract_words_from_transcript(japanese_transcript)
    return words
  else:
    print("EXTRACT UNIQUE WORDS ERROR: Failed to retrieve Japanese transcript.")
    return None
  
#test
# unique_words = extract_words_from_youtube("eXgMsg8WouU")
# print("Unique words extracted from video: " + str(len(unique_words)))
# for word in unique_words:
#   print(word.word + " " + word.reading + " " + word.translation)