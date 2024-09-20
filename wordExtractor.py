import subprocess
import re

def extractJapaneseWordsFromSentence(sentence):
  ichiranCommand = '(ichiran/dict:simple-segment "' + sentence + '")'
  cliCommand = ['ichiran-cli', '-e', ichiranCommand]
  result = subprocess.run(cliCommand, capture_output=True, text=True, encoding='utf-8')
  output_string = result.stdout

  # Use regex to find all kanji characters
  kanji_matches = re.findall(r'\w+\[', output_string)

  # Extract the kanji (remove the brackets)
  kanji_words = [match[:-1] for match in kanji_matches]

  # Filter out empty strings (if any)
  kanji_words = [word for word in kanji_words if word]

  print("Extracted words:")
  for word in kanji_words:
    print("- " + word)

  return kanji_words

# extractJapaneseWordsFromSentence("今日は、一日中図書館で勉強しました。")