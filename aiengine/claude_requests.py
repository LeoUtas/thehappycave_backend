import os, sys
from dotenv import load_dotenv
import anthropic


# ________________ HANDLE THE PATH THING ________________ #
# get the absolute path of the script's directory
script_path = os.path.dirname(os.path.abspath(__file__))
# get the parent directory of the script's directory
parent_path = os.path.dirname(script_path)
sys.path.append(parent_path)


from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from pathlib import Path
from dotenv import load_dotenv
from exception import CustomException
from database.database_handler import *


load_dotenv()
api_key = os.getenv("CLAUDE_THE_HAPPY_CAVE_ENGLISHTUTOR")
model = os.getenv("chosen_mistral_text_generation_model")
client = MistralClient(api_key=api_key)


# ________________ TEXT GENERATION ________________ #
def request_claude_response(model: str, prompt_input: str):
    try:

        # init_instruction = "Your name is Miss Puns-A-Lot. You are a female professional English tutor. Keep responses under 15 words and only in English. Your tutoring is tailored to IELTS speaking test practices. "

        client = anthropic.Client(api_key=api_key)

        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0.0,
            system="Respond only in Yoda-speak.",
            messages=[{"role": "user", "content": "How are you today?"}],
        )

        print(response.content)
        # return mistralai_response.choices[0].message.content

    except Exception as e:
        raise CustomException(e, sys)


if __name__ == "__main__":

    request_claude_response(model, "hi")
