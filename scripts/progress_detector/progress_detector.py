from ..anki.anki_connector import AnkiConnector
from ..anki.anki_note_adder import AnkiNoteAdder
from ..anki.anki_note import AnkiNote
from ..database.sentence_db_connector import SentenceDbConnector
from ..database.word_db_connector import WordDbConnector
from ..text_handling.japanese_sentence import JapaneseSentence
from ..text_handling.japanese_word import JapaneseWord
from ..database.video_db_connector import VideoDbConnector
from ..database.word_db_connector import WordDbConnector


class ProgressDetector:

    video_db_connector: VideoDbConnector
    sentence_db_connector: SentenceDbConnector
    anki_connector: AnkiConnector

    def __init__(self):
        self.video_db_connector = VideoDbConnector()
        self.sentence_db_connector = SentenceDbConnector()
        self.anki_connector = AnkiConnector()

    def update_progress(self):
        print("Updating progress...")
        self._update_word_progress()
        print("Word progress updated.")
        self._update_sentence_progress()
        print("Sentence progress updated.")
        self._unlock_sentences()
        print("Sentences unlocked.")
        self._unlock_youtube_videos()
        print("Videos unlocked.")

    def _update_word_progress(self):
        # get all anki cards
        anki_cards = self.anki_connector.get_all_anki_cards()

        # get all sentences
        word_connector = WordDbConnector()
        words = word_connector.get_all_words()

        # update the practice intervals sentences where it differs from anki
        words_with_updated_practice_intervals: list[JapaneseWord] = []
        for word in words:
            for anki_card in anki_cards:
                if word.anki_id == anki_card["note"]:
                    if word.practice_interval != anki_card["interval"]:
                        word.practice_interval = anki_card["interval"]
                        words_with_updated_practice_intervals.append(word)
                        break

        # update the practice intervals in the database
        for word in words_with_updated_practice_intervals:
            word_connector.update_word_practice_interval(word)

    def _update_sentence_progress(self):

        # get all anki cards
        anki_cards = self.anki_connector.get_all_anki_cards()

        # get all sentences
        sentences = self.sentence_db_connector.get_all_sentences()

        # update the practice intervals sentences where it differs from anki
        sentences_with_updated_practice_intervals: list[JapaneseSentence] = []
        for sentence in sentences:
            for anki_card in anki_cards:
                if sentence.anki_id == anki_card["note"]:
                    if sentence.practice_interval != anki_card["interval"]:
                        # print(
                        #     "diff detected. db: ",
                        #     sentence.practice_interval,  # prints 0 for all
                        #     " anki: ",
                        #     anki_card["interval"],
                        # )
                        sentence.practice_interval = anki_card["interval"]
                        sentences_with_updated_practice_intervals.append(sentence)
                        break

        # update the practice intervals in the database
        self.sentence_db_connector.update_sentence_practice_intervals(
            sentences_with_updated_practice_intervals
        )

    def _unlock_sentences(self):

        # get all locked sentences
        locked_sentences: list[JapaneseSentence] = (
            self.sentence_db_connector.get_locked_sentences()
        )

        # find sentences ready to unlock
        sentences_to_unlock = self._get_sentences_to_unlock(locked_sentences)
        if sentences_to_unlock is None or len(sentences_to_unlock) == 0:
            return

        # unlock them
        ids_of_sentences_to_unlock = [
            sentence.db_id for sentence in sentences_to_unlock
        ]
        self.sentence_db_connector.unlock_sentences(ids_of_sentences_to_unlock)

        # add them to anki in the prio deck!
        anki_note_adder = AnkiNoteAdder()
        anki_note_adder.add_sentences_to_priority_deck(sentences_to_unlock)

    def _get_sentences_to_unlock(self, locked_sentences):
        sentences_to_unlock: list[JapaneseSentence] = []
        for sentence in locked_sentences:
            words_ready = True
            for word in sentence.words:
                if not (word.practice_interval > 3):
                    words_ready = False
                    break
            if words_ready:
                sentences_to_unlock.append(sentence)
        return sentences_to_unlock

    def _unlock_youtube_videos(self):
        youtube_ids_of_videos_to_unlock = (
            self._get_youtube_ids_of_videos_that_can_be_unlocked()
        )
        for youtube_video_id in youtube_ids_of_videos_to_unlock:
            self.video_db_connector.unlock_video(youtube_video_id)

    def _get_youtube_ids_of_videos_that_can_be_unlocked(self):

        # get all locked videos
        locked_videos = self.video_db_connector.get_locked_videos()

        # for all locked videos, get all sentences
        youtube_ids_of_videos_to_unlock = []
        for video in locked_videos:
            sentences_in_video: list[JapaneseSentence] = (
                self.sentence_db_connector.get_sentences_for_video(video[0])
            )
            all_sentences_have_interval_of_4_or_more = True
            for sentence in sentences_in_video:
                if not (sentence.practice_interval > 4):
                    all_sentences_have_interval_of_4_or_more = False
                    break
            if all_sentences_have_interval_of_4_or_more:
                youtube_ids_of_videos_to_unlock.append(video[2])

        # return all videos that where all sentences have an interval of 4 or more
        return youtube_ids_of_videos_to_unlock
