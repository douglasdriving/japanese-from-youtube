from .anki.anki_word_adder import AnkiAdder
from .database.db_connector import DbConnector
from .text_handling.sentence_extractor import SentenceExtractor
from .text_handling.youtube_transcriber import YoutubeTranscriber
from .text_handling.sentence import JapaneseSentence
from .text_handling.word import JapaneseWord
from .text_handling.transcript_line import TranscriptLine


class YoutubeScraper:

    db_connector: DbConnector
    youtube_transcriber: YoutubeTranscriber
    anki_adder: AnkiAdder

    def __init__(self):
        self.db_connector = DbConnector()
        self.youtube_transcriber = YoutubeTranscriber()
        self.anki_adder = AnkiAdder()

    def scrape_video(self):

        youtube_video_id = self._get_valid_youtube_id_from_user()
        print("extracting sentences and words from youtube video...")
        transcript: list[TranscriptLine] = self.youtube_transcriber.transcribe(
            youtube_video_id
        )
        line_count = len(transcript)
        print("extracted ", line_count, " lines of text from video")
        sentence_extractor = SentenceExtractor(transcript)
        added_sentences: list[JapaneseSentence] = []
        for i, line in enumerate(transcript):
            print("processing line ", i + 1, " of ", line_count)
            sentence = sentence_extractor.extract_sentence(line.text)
            if sentence.words is not None:
                sentence.words = self._add_new_words(sentence.words)
            added_sentence = self.db_connector.add_sentence_if_new(sentence)
            if added_sentence:
                sentence.anki_id = self.anki_adder.add_sentence_note(added_sentence)
                added_sentences.append(added_sentence)

        # sentences: list[JapaneseSentence] = sentence_extractor.extract_sentences()
        # sentences = self._add_new_words_and_sentences(sentences)
        self._add_video_to_db(youtube_video_id, added_sentences)
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

    # def _add_new_words_and_sentences(self, sentences: list[JapaneseSentence]):
    #     added_sentences: list[JapaneseSentence] = []
    #     for sentence in sentences:
    #         sentence.words = self._add_new_words(sentence.words)
    #         added_sentence = self.db_connector.add_sentence_if_new(sentence)
    #         if added_sentence:
    #             anki_note_id = self.anki_adder.add_sentence_note(added_sentence)
    #             added_sentence.anki_id = anki_note_id
    #             added_sentences.append(added_sentence)
    #    return added_sentences

    def _add_new_words(self, words: list[JapaneseWord]):
        added_words: list[JapaneseWord] = []
        for word in words:
            word = self.db_connector.add_word_if_new_or_update_definition_if_existing(
                word
            )
            if word:
                if word.anki_id is None:
                    anki_id = self.anki_adder.add_word_note(word)
                    word.anki_id = anki_id
                added_words.append(word)
        return added_words
