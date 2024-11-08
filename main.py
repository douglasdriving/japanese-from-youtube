from scripts.youtube_scraper import YoutubeScraper
from scripts.data_cleaner.data_cleaner import DataCleaner
from scripts.progress_detector.progress_detector import ProgressDetector

# now: unlock sentences only after the word profficiency is high enough!

# ------------------------------------------------

# then, we need to check the locked sentences, and its status
# we will do that by checking the word profficiency of the sentence
# and then unlock it if it is high enough

# what if the locked sentences have already been added to anki?
# delete it, and then add it back in later when it is unlocked

# when we get sentences from db - utilize the crossrefs to also get the words

# lets go!


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
        while True:
            user_input = input("Press Enter to scrape another video or ESC to exit...")
            if user_input.lower() == "esc":
                break
            self.youtube_scraper.scrape_video()


main_program = MainProgram()
main_program.run()
