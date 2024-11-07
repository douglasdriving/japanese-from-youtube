from .anki.anki_word_adder import AnkiWordAdder
from .database.db_connector import DbConnector
from .text_handling.sentence_extractor import SentenceExtractor
from .text_handling.youtube_transcriber import YoutubeTranscriber
from .text_handling.sentence import JapaneseSentence
from .text_handling.japanese_word import JapaneseWord
from .text_handling.transcript_line import TranscriptLine


class YoutubeScraper:

    db_connector: DbConnector
    youtube_transcriber: YoutubeTranscriber
    anki_word_adder: AnkiWordAdder

    def __init__(self):
        self.db_connector = DbConnector()
        self.youtube_transcriber = YoutubeTranscriber()
        self.anki_word_adder = AnkiWordAdder()

    def scrape_video(self):
        youtube_video_id = self._get_valid_youtube_id_from_user()
        print("extracting sentences and words from youtube video...")
        transcript: list[TranscriptLine] = self.youtube_transcriber.transcribe(
            youtube_video_id
        )
        sentence_extractor = SentenceExtractor(transcript)
        sentences: list[JapaneseSentence] = sentence_extractor.extract_sentences()
        sentences_added_to_db: list[JapaneseSentence] = (
            self._add_new_words_and_sentences_to_db(sentences)
        )
        for sentence in sentences:
            if sentence.db_id is None:
                for sentence_added_to_db in sentences_added_to_db:
                    if sentence.sentence == sentence_added_to_db.sentence:
                        sentence.db_id = sentence_added_to_db.db_id
                        break
        self._add_video_to_db(youtube_video_id, sentences)
        self.anki_word_adder.add_words_and_sentences_to_anki(sentences_added_to_db)
        print("finished adding vocab to anki deck")

    def _add_video_to_db(
        self, youtube_video_id: str, sentences_in_video: list[JapaneseSentence]
    ):
        video_title = self.youtube_transcriber.get_video_title(youtube_video_id)
        video_db_id = self.db_connector.add_video(youtube_video_id, video_title)
        for sentence in sentences_in_video:
            self.db_connector.add_video_sentences_crossref(video_db_id, sentence.db_id)

    def _get_valid_youtube_id_from_user(self):
        print("enter a youtube video id")
        video_id = ""
        while len(video_id) != 11:
            print(
                "Invalid video id. please enter a valid youtube video id (11 characters)"
            )
            video_id = input()
        return video_id

    def _add_new_words_and_sentences_to_db(self, sentences: list[JapaneseSentence]):

        # add words and sentences
        added_sentences: list[JapaneseSentence] = []
        for sentence in sentences:
            added_words: list[JapaneseWord] = []
            for word in sentence.words:
                added_word = self.db_connector.add_word_if_new(word)
                if added_word:
                    added_words.append(added_word)
            added_sentence = self.db_connector.add_sentence_if_new(sentence)
            if added_sentence:
                added_sentence.words = added_words
                added_sentences.append(added_sentence)

        # add cross references
        for sentence in added_sentences:
            for word in sentence.words:
                self.db_connector.add_sentence_word_crossref(sentence.db_id, word.db_id)

        return added_sentences
