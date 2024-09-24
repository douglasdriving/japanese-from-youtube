import subprocess

def romanize_with_spaces(kana_text):
  ichiranCommand = '(ichiran:romanize "' + kana_text + '")'
  cliCommand = ['ichiran-cli', '-e', ichiranCommand]
  result = subprocess.run(cliCommand, capture_output=True, text=True, encoding='utf-8')
  output_string = result.stdout
  romanized_text = output_string.split('"')[1]
  romanized_text = romanized_text.replace('/', '&')
  romanized_text = romanized_text.replace('·', '-')
  return romanized_text

def romanize_with_underscore(kana_text):
  romanized_text = romanize_with_spaces(kana_text)
  romanized_text = romanized_text.replace(' ', '_')
  return romanized_text