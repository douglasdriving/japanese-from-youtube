# from scripts.youtube_to_anki_adder import add_new_vocab_from_youtube_to_anki_deck

# add_new_vocab_from_youtube_to_anki_deck()

from scripts.text_handling.jisho_connector import JishoConnector
from scripts.text_handling.sentence import JapaneseSentence

jisho_connector = JishoConnector()
sentence = jisho_connector.get_sentence_with_reading_and_definition("私は学生です")
print(sentence.sentence)
print(sentence.reading)
print(sentence.definition)
print(sentence.is_fully_defined())
