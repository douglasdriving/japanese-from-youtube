from scripts.youtube_scraper import YoutubeScraper
from scripts.data_cleaner.data_cleaner import DataCleaner
from scripts.progress_detector.progress_detector import ProgressDetector
from scripts.word_sorter.word_sorter import WordSorter
from scripts.sentence_adder.sentence_adder import SentenceAdder
import dotenv


class MainProgram:

    data_cleaner = DataCleaner()
    youtube_scraper = YoutubeScraper()
    progress_detector = ProgressDetector()
    word_sorter = WordSorter()
    manual_sentence_adder = SentenceAdder()

    def __init__(self):
        dotenv.load_dotenv()
        input("Please open Anki! Then press enter to continue...")

    def run(self):
        self.data_cleaner.clean_data_if_needed()
        self.progress_detector.update_progress()
        while True:
            user_input = input(
                "Press 1 to scrape a video, press 2 to insert a sentence manually, press esc to exit."
            )
            if user_input == "1":
                self.youtube_scraper.scrape_video()
                self.word_sorter.sort_words()
            elif user_input == "2":
                self.manual_sentence_adder.add_sentence_manually()
            elif user_input == "esc":
                break


main_program = MainProgram()
main_program.run()
