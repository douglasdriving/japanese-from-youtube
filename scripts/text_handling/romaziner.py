import subprocess


class Romanizer:

    def __init__(self):
        pass

    def romanize_with_spaces(self, kana_text: str):
        ichiranCommand = '(ichiran:romanize "' + kana_text + '")'
        cliCommand = ["ichiran-cli", "-e", ichiranCommand]
        result = subprocess.run(
            cliCommand, capture_output=True, text=True, encoding="utf-8"
        )
        output_string = result.stdout
        romanized_text = output_string.split('"')[1]
        romanized_text = romanized_text.replace("/", "&")
        romanized_text = romanized_text.replace("·", "-")
        romanized_text = romanized_text.replace("\\", "_")
        return romanized_text

    def romanize_with_underscore(self, kana_text):
        romanized_text = self.romanize_with_spaces(kana_text)
        romanized_text = romanized_text.replace(" ", "_")
        return romanized_text
