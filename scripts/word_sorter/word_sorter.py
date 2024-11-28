from ..database.db_connector import DbConnector
from ..anki.anki_deleter import AnkiDeleter
from ..anki.anki_adder import AnkiAdder
from ..text_handling.word import JapaneseWord


class WordSorter:

    db_connector = DbConnector()
    anki_deleter = AnkiDeleter()
    anki_adder = AnkiAdder()

    def __init__(self):
        pass

    def sort_words(self):
        print("Sorting words in Anki by popularity...")
        words_without_progress = self.db_connector.get_words_without_progress()
        word_popularity = self.db_connector.get_words_popilarity(words_without_progress)
        sorted_words_popularity = sorted(
            word_popularity.items(), key=lambda x: x[1], reverse=True
        )
        sorted_words: list[JapaneseWord] = [word[0] for word in sorted_words_popularity]
        sorted_word_anki_ids = [word.anki_id for word in sorted_words]
        self.anki_deleter.delete_notes(sorted_word_anki_ids)
        self.anki_adder.add_words_and_mark_in_db(sorted_words)
        print("Done sorting words in Anki by popularity!")
