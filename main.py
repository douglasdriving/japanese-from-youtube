# from scripts.youtube_to_anki_adder import add_new_vocab_from_youtube_to_anki_deck

# add_new_vocab_from_youtube_to_anki_deck()

from scripts.text_handling.sentence_data_extractor import SentenceDataExtractor
from scripts.text_handling.translator import translate_jp_to_en
from scripts.youtube_transcriber import (
    get_japanese_transcript_as_single_text,
    get_japanese_transcript,
    remove_parenthesis_and_text_inside_it,
)

transcript = get_japanese_transcript("GUqFU5u7rLQ")
for line in transcript:
    sentence = line["text"]
    sentence = remove_parenthesis_and_text_inside_it(sentence)
    translation = translate_jp_to_en(sentence)
    print(sentence)
    print(translation)

# okay so, a struggle here is that these translations are not perfect.
# its google tranlate and its a bit shitty. but I wounder if the problem might also just be that we are translating sentence by sentence


# okay so here, we ALREADY HAVE OUR SENTENCES. so no need to break them out.

# sentence_data_extractor = SentenceDataExtractor(transcript)
# sentences = sentence_data_extractor.extract_sentences_not_in_db()
# for sentence in sentences:
#     print(sentence.sentence)
#     print(sentence.definition)
#     print(sentence.audio_file)
