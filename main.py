from scripts.youtube_scraper import YoutubeScraper
from scripts.data_cleaner.data_cleaner import DataCleaner
from scripts.progress_detector.progress_detector import ProgressDetector


class MainProgram:

    data_cleaner: DataCleaner
    youtube_scraper: YoutubeScraper
    progress_detector: ProgressDetector

    def __init__(self):
        self.data_cleaner = DataCleaner()
        self.youtube_scraper = YoutubeScraper()
        self.progress_detector = ProgressDetector()

    def run(self):
        self.data_cleaner.clean_data()
        self.progress_detector.update_progress()
        self.youtube_scraper.scrape_video()
        input("Program finished. Press Enter to exit...")


main_program = MainProgram()
main_program.run()
