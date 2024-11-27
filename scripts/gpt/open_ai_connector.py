from openai import OpenAI
from ..text_handling.sentence import JapaneseSentence
from ..text_handling.word import JapaneseWord
import json
import dotenv


class OpenAiConnector:

    client: OpenAI

    def __init__(self):
        dotenv.load_dotenv()
        self.client = OpenAI()

    def get_sentence_data(self, sentence_text: str):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": "You are a Japanese translator. You will give the user information about Japanese sentences. The user will provide you with a sentence, and you will return a JSON object containing information about that sentence. The JSON object will contain these fields:\n\n- text: the original sentence sent by the user\n- romaji: the sentence written in romaji\n- translation: the sentence translated into English\n- words: an array of each word in the sentence\n\nEach word in the array should be an object with these fields:\n\n- text: the word in kana\n- reading: the reading of the word in furigana\n- romaji: the word in romaji\n- translation: the English translation/definition of the word",
                            }
                        ],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": sentence_text}],
                    },
                ],
                temperature=0.18,
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            print(
                "gpt processed sentence with total tokens: ",
                response.usage.total_tokens,
            )
            sentence_json = json.loads(response.choices[0].message.content)
        except Exception as e:
            print("ERROR GETTING SENTENCE DATA: ", e)
            return None
        sentence = self._turn_sentence_json_into_sentence(sentence_json)
        if sentence is None:
            print("ERROR GETTING SENTENCE DATA: sentence json returned None")
        return sentence

    def _turn_sentence_json_into_sentence(self, sentence_json):
        try:
            self._check_sentence_json(sentence_json)
        except ValueError as e:
            print("ERROR WITH SENTENCE RETURNED FROM GPT: ", e)
            return None
        sentence = JapaneseSentence(
            sentence_json["text"],
            sentence_json["translation"],
            romaji=sentence_json["romaji"],
            gpt_generated=True,
        )
        words_json = sentence_json.get("words", [])
        words: list[JapaneseWord] = []
        for word in words_json:
            words.append(
                JapaneseWord(
                    word=word["text"],
                    reading=word["reading"],
                    definition=word["translation"],
                    romaji=word["romaji"],
                )
            )
        sentence.words = words
        return sentence

    def _check_sentence_json(self, sentence_json: json):
        if "text" not in sentence_json:
            raise ValueError("text not found in sentence json")
        if "romaji" not in sentence_json:
            raise ValueError("romaji not found in sentence json")
        if "translation" not in sentence_json:
            raise ValueError("translation not found in sentence json")
        if "words" not in sentence_json:
            raise ValueError("words not found in sentence json")
        words = sentence_json.get("words", [])
        if not isinstance(words, list):
            raise ValueError("words is not a list in sentence json")
        for word in words:
            if "text" not in word:
                raise ValueError("text not found in word json")
            if "reading" not in word:
                raise ValueError("reading not found in word json")
            if "romaji" not in word:
                raise ValueError("romaji not found in word json")
            if "translation" not in word:
                raise ValueError("translation not found in word json")
        return True

    def convert_to_romaji(self, sentence_text: str):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": "You are a Japanese romaji converter. You will give the user the romaji of a Japanese sentence. The user will provide you with a japanese sentence in kana, and you will return the romaji version of that sentence. Only provide the romaji text back, and nothing else",
                            }
                        ],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": sentence_text}],
                    },
                ],
                temperature=0.18,
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            print(
                "gpt processed romaji with total tokens: ",
                response.usage.total_tokens,
            )
            romaji = response.choices[0].message.content
        except Exception as e:
            print("ERROR GETTING ROMAJI: ", e)
            return None
        return romaji
