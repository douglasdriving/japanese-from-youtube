from ..anki.anki_getter import AnkiGetter
from ..database.db_connector import DbConnector
from ..text_handling.sentence import JapaneseSentence
from ..text_handling.word import JapaneseWord
from ..database.video_db_connector import VideoDbConnector


class ProgressDetector:

    video_db_connector: VideoDbConnector

    def __init__(self):
        self.video_db_connector = VideoDbConnector()

    def update_progress(self):
        self._update_card_progress()
        youtube_ids_of_videos_to_unlock = (
            self._get_youtube_ids_of_videos_that_can_be_unlocked()
        )
        for youtube_video_id in youtube_ids_of_videos_to_unlock:
            self.video_db_connector.unlock_video(youtube_video_id)

    def _update_card_progress(self):

        db_connector = DbConnector()
        anki_getter = AnkiGetter()

        # get all anki cards
        anki_cards = anki_getter.get_all_cards()
        anki_card_dict = {anki_card["note"]: anki_card for anki_card in anki_cards}

        # words
        words = db_connector.get_all_words()
        words_with_updated_practice_intervals: list[JapaneseWord] = []
        for word in words:
            if word.anki_id in anki_card_dict:
                true_interval = anki_card_dict[word.anki_id]["interval"]
                if word.practice_interval != true_interval:
                    word.practice_interval = true_interval
                    words_with_updated_practice_intervals.append(word)
        db_connector.update_word_practice_intervals(
            words_with_updated_practice_intervals
        )

        # update the practice intervals sentences where it differs from anki
        sentences = db_connector.get_all_sentences()
        sentences_with_updated_practice_intervals: list[JapaneseSentence] = []
        for sentence in sentences:
            if sentence.anki_id in anki_card_dict:
                true_interval = anki_card_dict[sentence.anki_id]["interval"]
                if sentence.practice_interval != true_interval:
                    sentence.practice_interval = true_interval
                    sentences_with_updated_practice_intervals.append(sentence)
        db_connector.update_sentence_practice_intervals(
            sentences_with_updated_practice_intervals
        )

    def _get_youtube_ids_of_videos_that_can_be_unlocked(self):

        # get all locked videos
        locked_videos = self.video_db_connector.get_locked_videos()

        # for all locked videos, get all sentences
        youtube_ids_of_videos_to_unlock = []
        for video in locked_videos:
            sentences_in_video: list[JapaneseSentence] = (
                self.video_db_connector.get_sentences_for_video(video[0])
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
