from scripts.youtube_to_anki_adder import add_new_vocab_from_youtube_to_anki_deck
from scripts.data_cleaner import DataCleaner

cleaner = DataCleaner()
cleaner.clean_database()

# add_new_vocab_from_youtube_to_anki_deck()
input("Program finished. Press Enter to exit...")
