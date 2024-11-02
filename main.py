from scripts.youtube_scraper import YoutubeScraper

# from scripts.data_cleaner.data_cleaner import DataCleaner

# cleaner = DataCleaner()
# cleaner.clean_data()
youtube_scraper = YoutubeScraper()
youtube_scraper.extract_youtube_vocab()


# from scripts.youtube_transcriber import get_transcript

# transcript = get_transcript("QnLABAkqxNs")
# for line in transcript:
#     print(line.text)


input("Program finished. Press Enter to exit...")
