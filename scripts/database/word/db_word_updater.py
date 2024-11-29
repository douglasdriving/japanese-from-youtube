from ..db_connector import DbConnector
from ...text_handling.word import JapaneseWord
import sqlite3


class DbWordUpdater:

    connector = DbConnector()

    def __init__(self):
        pass

    def add_definition_to_word_if_new(self, word_id, new_definition: str):
        self.connector.cursor.execute(
            """
            SELECT definition FROM vocabulary WHERE id = (?)
            """,
            (word_id,),
        )
        current_definition = self.connector.cursor.fetchone()
        if current_definition is None:
            print(
                f"ERROR: Word with id {word_id} does not exist. cant update its definition"
            )
            return ""
        current_definition: str = current_definition[0]
        definitions = current_definition.split(";")
        for definition in definitions:
            if definition.strip() == new_definition.strip():
                return current_definition
        updated_definition = f"{current_definition}; {new_definition}"
        self.connector.cursor.execute(
            """
            UPDATE vocabulary
            SET definition = ?
            WHERE id = ?
            """,
            (updated_definition, word_id),
        )
        self.connector.connection.commit()
        print(f"Added definition '{new_definition}' to word with id {word_id}")
        return updated_definition

    def update_word_practice_intervals(self, words: list[JapaneseWord]):
        for word in words:
            self.connector.cursor.execute(
                """
                UPDATE vocabulary
                SET practice_interval = ?
                WHERE id = ?
                """,
                (word.practice_interval, word.db_id),
            )
            self.connector.connection.commit()
            print(
                f"Updated practice interval for word {word.word} to {word.practice_interval}"
            )

    def change_word_definition(self, word_id: int, new_definition: str):
        try:
            self.connector.cursor.execute(
                """
                    UPDATE vocabulary
                    SET definition = ?
                    WHERE id = ?
                    """,
                (new_definition, word_id),
            )
            self.connector.connection.commit()
            print(
                f"Updated definition for word with id {word_id} to '{new_definition}'"
            )
        except sqlite3.Error as error:
            print("ERROR UPDATING WORD DEFINITION: ", error)

    def update_anki_note_id(self, table_name: str, id: int, anki_id: int):
        if id is None:
            print(
                f"Warning: Sentence has no database ID. Skipping changing the anki ID."
            )
            return
        self.connector.cursor.execute(
            f"""
            UPDATE {table_name}
            SET anki_note_id = ?
            WHERE id = ?
            """,
            (anki_id, id),
        )
        self.connector.connection.commit()
        print(f"Updated anki_note_id for {id} to {anki_id} in {table_name}")
