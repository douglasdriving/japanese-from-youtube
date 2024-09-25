# from scripts.youtube_to_anki_adder import add_new_vocab_from_youtube_to_anki_deck

# add_new_vocab_from_youtube_to_anki_deck()

from scripts.text_handling.jisho_connector import JishoConnector

jisho_connector = JishoConnector()
sentence = jisho_connector.get_sentence_with_reading_and_definition(
    "今日は一日中図書館で勉強しました"
)
print(sentence.sentence)
print(sentence.reading)
print(sentence.definition)
