# connects to the jisho api to get japanese word data
from jisho_api.sentence import Sentence
from .sentence import JapaneseSentence


class JishoConnector:

    def __init__(self):
        pass

    def get_sentence_with_reading_and_definition(self, kana_sentence: str):

        word_result = Sentence.request(kana_sentence)
        if word_result == None:
            print("ERROR: No data found for the sentence. Error: ", word_result.error)
            return None

        data = word_result.data[0]
        reading = data.japanese
        definition = data.en_translation
        japanese_sentence = JapaneseSentence(kana_sentence, reading, definition)
        return japanese_sentence
