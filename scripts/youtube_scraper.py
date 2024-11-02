from .anki.anki_word_adder import add_words_and_sentences_to_anki
from .database.vocabulary_connector import VocabularyConnector
from .text_handling.sentence_data_extractor import SentenceDataExtractor
from .youtube_transcriber import get_transcript
from .text_handling.sentence import JapaneseSentence
from .text_handling.japanese_word import JapaneseWord
from .transcript_line import TranscriptLine


class YoutubeScraper:

    vocabulary_connector: VocabularyConnector

    def __init__(self):
        self.vocabulary_connector = VocabularyConnector()

    def extract_youtube_vocab(self):
        video_id = self._get_valid_youtube_id_from_user()
        print("extracting sentences and words from youtube video...")
        transcript: list[TranscriptLine] = get_transcript(video_id)
        sentence_data_extractor = SentenceDataExtractor(transcript)
        sentences = sentence_data_extractor.extract_sentences_not_in_db()
        sentences_added_to_db = self._add_words_and_sentences_to_db(sentences)
        add_words_and_sentences_to_anki(sentences_added_to_db)
        print("finished adding vocab to anki deck")

    def _get_valid_youtube_id_from_user(self):
        print("enter a youtube video id")
        video_id = ""
        while len(video_id) != 11:
            print(
                "Invalid video id. please enter a valid youtube video id (11 characters)"
            )
            video_id = input()
        return video_id

    def _add_words_and_sentences_to_db(self, sentences: list[JapaneseSentence]):
        added_sentences: list[JapaneseSentence] = []
        for sentence in sentences:
            added_words: list[JapaneseWord] = []
            for word in sentence.words:
                added_word = self.vocabulary_connector.add_word_if_new(word)
                if added_word:
                    added_words.append(added_word)
            added_sentence = self.vocabulary_connector.add_sentence_if_new(sentence)
            if added_sentence:
                added_sentence.words = added_words
                added_sentences.append(added_sentence)
        return added_sentences
