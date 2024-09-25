# connects to the jisho api to get japanese word data
from jisho_api.sentence import Sentence
from .sentence import JapaneseSentence


class JishoConnector:

    def __init__(self):
        pass

    def get_sentence_with_reading_and_definition(self, kana_sentence: str):

        # lol, this does NOT translate sentences. it just gets example sentences for words
        # we need to use something else, like google translate
        # also, is reading necessary? maybe not.
        # i mean, if we want it to be perfect we want to do the same thing. get the reading for the whole sentence and then use that for audio
        # idk...

        word_result = Sentence.request(kana_sentence)
        if word_result == None:
            print("ERROR: No data found for the sentence. Error: ", word_result.error)
            return None

        data = word_result.data[0]
        reading = data.japanese
        definition = data.en_translation
        japanese_sentence = JapaneseSentence(kana_sentence, reading, definition)
        return japanese_sentence
