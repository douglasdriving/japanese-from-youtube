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
        # before we start scraping, detect our progress on current videos, and inform user if they unlocked a new video!
        # then we update all sentence cards from anki with the new progress
        # then we check if one of the videos that was locked is now profficient enough
        # then we unlock it! and inform the user!
        self.youtube_scraper.scrape_video()
        input("Program finished. Press Enter to exit...")


main_program = MainProgram()
main_program.run()
