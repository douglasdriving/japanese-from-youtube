from .anki.anki_adder import AnkiAdder
from .database.db_connector import DbConnector
from .database.word.db_word_adder import DbWordAdder
from .database.sentence.db_sentence_adder import DbSentenceAdder
from .database.video.db_video_adder import DbVideoAdder
from .text_handling.youtube_transcriber import YoutubeTranscriber
from .text_handling.sentence import JapaneseSentence
from .text_handling.word import JapaneseWord
from .text_handling.transcript_line import TranscriptLine
from .sentence_adder.sentence_adder import SentenceAdder


class YoutubeScraper:

    db_connector: DbConnector
    youtube_transcriber: YoutubeTranscriber
    anki_adder: AnkiAdder
    word_adder = DbWordAdder()
    db_sentence_adder = DbSentenceAdder()
    db_video_adder = DbVideoAdder()
    sentence_adder = SentenceAdder()

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
        added_sentences: list[JapaneseSentence] = []
        for i, line in enumerate(transcript):
            print("processing line ", i + 1, " of ", line_count)
            self.sentence_adder.add_sentence(line.text)
        self._add_video_to_db(youtube_video_id, added_sentences)
        print("finished adding vocab to anki deck")

    def _add_video_to_db(
        self, youtube_video_id: str, sentences_in_video: list[JapaneseSentence]
    ):
        video_title = self.youtube_transcriber.get_video_title(youtube_video_id)
        video_db_id = self.db_video_adder.add_video(youtube_video_id, video_title)
        for sentence in sentences_in_video:
            self.db_video_adder.add_video_sentences_crossref(
                video_db_id, sentence.db_id
            )

    def _get_valid_youtube_id_from_user(self):
        print("enter a youtube video id")
        video_id = ""
        while len(video_id) != 11:
            print(
                "Invalid video id. please enter a valid youtube video id (11 characters)"
            )
            video_id = input()
        return video_id
