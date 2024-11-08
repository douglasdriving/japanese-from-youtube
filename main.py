from scripts.youtube_scraper import YoutubeScraper
from scripts.data_cleaner.data_cleaner import DataCleaner
from scripts.progress_detector.progress_detector import ProgressDetector

# now: unlock sentences only after the word profficiency is high enough!

# ------------------------------------------------

# when we unlock the sentence, we should also add the anki card for it!
# and add that card to the top of the deck.
# PROBLEM: we cant change to card order. ankis algorithm determines that
# so what we probably have to do is add all sentence cards by default when we scrape them, but also SUSPEND those cards (if they are not unlocked)
# then, when we unlock the sentence, we unsuspend the card card

# what if the locked sentences have already been added to anki?
# delete it, and then add it back in later when it is unlocked

# when we are cleaning anki and want to add sentence cards that are missing from the db, make sure we dont add the locked ones

# when we get sentences from db - utilize the crossrefs to also get the words

# make sure that sentences are not added to anki initially during the youtube scraping

# lets go!

# -------- BUGS ------------


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
