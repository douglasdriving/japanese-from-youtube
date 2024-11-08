import sqlite3
import re
import os
from scripts.text_handling.speech_synthesizer import SpeechSynthesizer
from .anki_cleaner import AnkiCleaner
from ..database.word_db_connector import WordDbConnector
from ..anki.anki_connector import AnkiConnector
from ..text_handling.word_extractor import WordExtractor
from ..text_handling.japanese_word import JapaneseWord
from ..text_handling.japanese_sentence import JapaneseSentence
from ..database.sentence_db_connector import SentenceDbConnector


class DataCleaner:

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor
    word_db_connector: WordDbConnector
    anki_connector: AnkiConnector
    sentence_db_connector: SentenceDbConnector
    speech_synthesizer: SpeechSynthesizer

    def __init__(self):
        self.connection = sqlite3.connect("vocabulary.db")
        self.cursor = self.connection.cursor()
        self.word_db_connector = WordDbConnector()
        self.anki_connector = AnkiConnector()
        self.sentence_db_connector = SentenceDbConnector()
        self.speech_synthesizer = SpeechSynthesizer()

    def clean_data(self):
        print("Cleaning data...")
        self._add_missing_crossrefs()
        self._clean_audio_file_names()
        anki_cleaner = AnkiCleaner()
        anki_cleaner.clean()
        self._add_missing_anki_ids()

    ## audio file name cleaning - separate class?
    def _clean_audio_file_names(self):
        print("Cleaning audio file names...")
        self._clean_word_audio_file_names()
        self._clean_sentence_audio_file_names()
        self._delete_all_audio_files_with_wrong_pattern()

    def _clean_word_audio_file_names(self):
        words = self.word_db_connector.get_all_words()
        audio_file_pattern = self._get_audio_file_pattern()
        for word in words:
            if not os.path.exists(word.audio_file_path):
                self._make_new_audio_for_word(word)
            elif not audio_file_pattern.match(word.audio_file_path):
                self._rename_word_audio(word)

    def _rename_word_audio(self, word: JapaneseWord):
        new_file_path = (
            f"./audios/w{self.speech_synthesizer.get_highest_audio_id(False)+1}.wav"
        )
        self.word_db_connector.update_audio_file_path(new_file_path, word.db_id)
        self.connection.commit()
        os.rename(word.audio_file_path, new_file_path)
        print(f"Renamed {word.audio_file_path} to {new_file_path}")

    def _make_new_audio_for_word(self, word: JapaneseWord):
        new_audio_file = self.speech_synthesizer.save_jp_text_as_audio(word.word, False)
        self.word_db_connector.update_audio_file_path(word.db_id, new_audio_file)
        print(f"Added audio file for {word.word} to {new_audio_file}")

    def _get_audio_file_pattern(self, audio_type="word"):
        if audio_type == "word":
            return re.compile(r"./audios/w\d+\.wav")
        if audio_type == "sentence":
            return re.compile(r"./audios/s\d+\.wav")
        print("Invalid audio type: ", audio_type)
        return None

    def _clean_sentence_audio_file_names(self):
        sentences = self.sentence_db_connector.get_all_sentences()
        audio_file_pattern = self._get_audio_file_pattern("sentence")
        for sentence in sentences:
            if not os.path.exists(sentence.audio_file_path):
                self._make_new_audio_for_sentence(sentence)
            elif not audio_file_pattern.match(sentence.audio_file_path):
                self._rename_sentence_audio(sentence)

    def _rename_sentence_audio(self, sentence: JapaneseSentence):
        new_file_path = (
            f"./audios/s{self.speech_synthesizer.get_highest_audio_id(True)+1}.wav"
        )
        self.sentence_db_connector.update_audio_file_path(new_file_path, sentence.db_id)
        os.rename(sentence.audio_file_path, new_file_path)
        print(f"Renamed {sentence.audio_file_path} to {new_file_path}")

    def _make_new_audio_for_sentence(self, sentence: JapaneseSentence):
        new_audio_file = self.speech_synthesizer.save_jp_text_as_audio(
            sentence.sentence, True
        )
        self.sentence_db_connector.update_audio_file_path(
            sentence.db_id, new_audio_file
        )
        print(f"Added audio file for {sentence.sentence} to {new_audio_file}")

    def _delete_all_audio_files_with_wrong_pattern(self):
        audio_files = os.listdir("./audios")
        for audio_file in audio_files:
            if not re.match(r"s\d+\.wav", audio_file) and not re.match(
                r"w\d+\.wav", audio_file
            ):
                os.remove(f"./audios/{audio_file}")
                print(
                    f"Deleted {audio_file} from audios folder since it is not in correct format"
                )

    ## anki id and crossref adding
    def _add_missing_anki_ids(self):

        def update_words(all_anki_notes):
            print("Updating words...")
            words_to_update = self.word_db_connector.get_words_without_anki_note_id()
            for word in words_to_update:
                anki_note = next(
                    (
                        note
                        for note in all_anki_notes
                        if note["fields"]["Back"]["value"] == word.definition
                    ),
                    None,
                )
                if anki_note is None:
                    print(
                        f"Could not find anki note for word: {word.definition}, unable to update anki id"
                    )
                else:
                    anki_id = anki_note["noteId"]
                    self.word_db_connector.update_anki_note_id(
                        "vocabulary", word.db_id, anki_id
                    )

        def update_sentences(all_anki_notes):
            print("Updating sentences...")
            sentences_to_update = (
                self.sentence_db_connector.get_sentences_without_anki_note_id()
            )
            for sentence in sentences_to_update:
                anki_note = next(
                    (
                        note
                        for note in all_anki_notes
                        if note["fields"]["Back"]["value"]
                        .split("\n")[0]
                        .split("<br>")[0]
                        == sentence.definition
                    ),
                    None,
                )
                if anki_note is None:
                    print(
                        f"Could not find anki note for sentence: {sentence.definition}, unable to update anki id"
                    )
                else:
                    anki_id = anki_note["noteId"]
                    self.word_db_connector.update_anki_note_id(
                        "sentences", sentence.db_id, anki_id
                    )

        print("Adding missing anki ids...")
        anki_notes = self.anki_connector.get_all_notes()
        update_words(anki_notes)
        update_sentences(anki_notes)

    def _add_missing_crossrefs(self):
        sentences = self.sentence_db_connector.get_all_sentences()
        word_extractor = WordExtractor()
        for sentence in sentences:
            is_missing_crossrefs = sentence.words is None or len(sentence.words) == 0
            if is_missing_crossrefs:
                words: list[JapaneseWord] = word_extractor.extract_words_from_text(
                    sentence.sentence
                )
                if words is None or len(words) == 0:
                    self.sentence_db_connector.delete_sentence(sentence.db_id)
                else:
                    for word in words:
                        if word.db_id is None:
                            word = self.word_db_connector.add_word_if_new(word)
                        if not word:
                            print(f"Could not add word because it is None")
                        elif word.db_id is not None:
                            self.sentence_db_connector.add_sentence_word_crossref(
                                sentence.db_id, word.db_id
                            )
                        else:
                            print(
                                f"Could not add crossref for word: {word.word} because it does not have a db id"
                            )
