from scripts.youtube_scraper import YoutubeScraper
from scripts.data_cleaner.data_cleaner import DataCleaner
from scripts.progress_detector.progress_detector import ProgressDetector
from scripts.word_sorter.word_sorter import WordSorter
import dotenv


class MainProgram:

    data_cleaner = DataCleaner()
    youtube_scraper = YoutubeScraper()
    progress_detector = ProgressDetector()
    word_sorter = WordSorter()

    def __init__(self):
        dotenv.load_dotenv()
        input("Please open Anki! Then press enter to continue...")

    def run(self):
        self.data_cleaner.clean_data()
        self.progress_detector.update_progress()
        self.youtube_scraper.scrape_video()
        self.word_sorter.sort_words()
        while True:
            user_input = input("Press Enter to scrape another video or ESC to exit...")
            if user_input.lower() == "esc":
                break
            self.youtube_scraper.scrape_video()
            self.word_sorter.sort_words()


main_program = MainProgram()
main_program.run()
