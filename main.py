from scripts.youtube_scraper import YoutubeScraper
from scripts.data_cleaner.data_cleaner import DataCleaner
from scripts.progress_detector.progress_detector import ProgressDetector
import dotenv

# CURRENTLY IMPLEMENTING: SENTENCE UNLOCKS
# TODO make sure sentences are in anki only after then have been unlocked (top of stack)
# TODO cleaner removes all sentences from ANKI that are not unlocked yet.


class MainProgram:

    data_cleaner: DataCleaner
    youtube_scraper: YoutubeScraper
    progress_detector: ProgressDetector

    def __init__(self):
        dotenv.load_dotenv()
        input("Please open Anki! Then press enter to continue...")
        self.data_cleaner = DataCleaner()
        self.youtube_scraper = YoutubeScraper()
        self.progress_detector = ProgressDetector()

    def run(self):
        self.data_cleaner.clean_data()
        self.progress_detector.update_progress()
        self.youtube_scraper.scrape_video()
        while True:
            user_input = input("Press Enter to scrape another video or ESC to exit...")
            if user_input.lower() == "esc":
                break
            self.youtube_scraper.scrape_video()


main_program = MainProgram()
main_program.run()
