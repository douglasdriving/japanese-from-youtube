from ..anki.anki_connector import AnkiConnector
from ..database.db_connector import DbConnector
from ..text_handling.sentence import JapaneseSentence
from ..database.video_db_connector import VideoDbConnector


class ProgressDetector:

    video_db_connector: VideoDbConnector

    def __init__(self):
        self.video_db_connector = VideoDbConnector()

    def update_progress(self):
        self._update_sentence_progress()
        youtube_ids_of_videos_to_unlock = (
            self._get_youtube_ids_of_videos_that_can_be_unlocked()
        )
        for youtube_video_id in youtube_ids_of_videos_to_unlock:
            self.video_db_connector.unlock_video(youtube_video_id)

    def _update_sentence_progress(self):

        # get all anki cards
        anki_connector = AnkiConnector()
        anki_cards = anki_connector.get_all_anki_cards()

        # get all sentences
        db_connector = DbConnector()
        sentences = db_connector.get_all_sentences()

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
