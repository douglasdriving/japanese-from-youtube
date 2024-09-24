import sqlite3
from ..text_handling.japanese_word import JapaneseWord

class VocabularyConnector:
  def __init__(self):
    self.connection = sqlite3.connect('vocabulary.db')
    self.cursor = self.connection.cursor()
    
  def add_word(self, word:JapaneseWord, audio_file_path:str):
    if(not word.is_fully_defined()):
      print('ERROR: Word is not fully defined. Not adding to database.')
      print(word)
      return
    try:
      self.cursor.execute('''
      INSERT INTO vocabulary (word, reading, definition, audio_file_path)
      VALUES (?, ?, ?, ?)
      ''', (word.word, word.reading, word.definition, audio_file_path)
      )
      self.connection.commit()
    except sqlite3.Error as error:
      print("ERROR INSERTING WORD: ", error)
  
  def clear_database(self):
    self.cursor.execute('''
    DELETE FROM vocabulary
    ''')
    self.connection.commit()