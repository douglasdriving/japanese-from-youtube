from scripts.youtube_scraper import YoutubeScraper
from scripts.data_cleaner.data_cleaner import DataCleaner


class MainProgram:

    data_cleaner: DataCleaner
    youtube_scraper: YoutubeScraper

    def __init__(self):
        self.data_cleaner = DataCleaner()
        self.youtube_scraper = YoutubeScraper()

    def run(self):
        self.data_cleaner.clean_data()
        self.youtube_scraper.scrape_video()
        input("Program finished. Press Enter to exit...")


main_program = MainProgram()
main_program.run()
