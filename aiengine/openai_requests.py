import os, sys


# ________________ HANDLE THE PATH THING ________________ #
# get the absolute path of the script's directory
script_path = os.path.dirname(os.path.abspath(__file__))
# get the parent directory of the script's directory
parent_path = os.path.dirname(script_path)
sys.path.append(parent_path)


from openai import OpenAI
from exception import CustomException


class OpenaiAPI:

    def __init__(
        self,
        api_key,
        model_speech_to_text,
        model_text_generation,
        model_text_to_speech,
    ):
        self.api_key = api_key
        self.model_speech_to_text = model_speech_to_text
        self.model_text_generation = model_text_generation
        self.model_text_to_speech = model_text_to_speech

        self.client = OpenAI(api_key=self.api_key)

    # ________________ BACKEND FOR OPENAICHATBOT _________________ #
    # ________________ CONVERT SPEECH TO TEXT ________________ #
    def convert_speech_to_text(self, audio_input, response_format="text"):
        try:

            transcript = self.client.audio.transcriptions.create(
                model=self.model_speech_to_text,
                language="en",
                file=audio_input,
                response_format=response_format,
            )

            return transcript

        except Exception as e:
            raise CustomException(e, sys)

    # ________________ TEXT GENERATION ________________ #
    def request_openai_text_generation(
        self,
        messages: dict,
    ):
        try:

            openai_response = self.client.chat.completions.create(
                model=self.model_text_generation, messages=messages
            )

            return openai_response.choices[0].message.content

        except Exception as e:
            raise CustomException(e, sys)

    # ________________ CONVERT TEXT TO SPEECH USING OPENAI ________________ #
    def convert_text_to_speech(self, voice: str, text_input: str):
        try:

            response = self.client.audio.speech.create(
                model=self.model_text_to_speech,
                voice=voice,
                input=text_input,
            )

            return response.content

        except Exception as e:
            raise CustomException(e, sys)

    # _____________ BACKEND FOR TODOTODAY _____________ #
    # ________________ TEXT GENERATION ________________ #
    def request_openai_response_for_todotoday(self, role: str, prompt: str):
        try:
            ai_response = self.client.chat.completions.create(
                model=self.model_text_generation,
                messages=[
                    {
                        "role": role,
                        "content": prompt,
                    }
                ],
            )

            return ai_response.choices[0].message.content

        except Exception as e:
            raise CustomException(e, sys)

    # _____________ BACKEND FOR BIRD CLASSIFICATION _____________ #
    # ________________ TEXT GENERATION ________________ #
    def request_openai_response_for_funfact(self, role: str, prompt: str):
        try:
            ai_response = self.client.chat.completions.create(
                model=self.model_text_generation,
                messages=[
                    {
                        "role": role,
                        "content": prompt,
                    }
                ],
            )

            return ai_response.choices[0].message.content

        except Exception as e:
            raise CustomException(e, sys)
