# _______ BACKEND FOR TODOTODAY _______ #

import sys, os
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel

# ________________ HANDLE THE PATH THING ________________ #
# get the absolute path of the script's directory
script_path = os.path.dirname(os.path.abspath(__file__))
# get the parent directory of the script's directory
parent_path = os.path.dirname(script_path)
sys.path.append(parent_path)


from aiengine.openai_requests import OpenaiAPI
from exception import CustomException


class Item(BaseModel):
    percentage_done: float


# ________________ CONFIG OPENAI API ________________ #
load_dotenv()
api_key = os.getenv("TODOTODAY_API_KEY")
model_speech_to_text = os.getenv("chosen_model_speech_to_text")
model_text_generation = os.getenv("chosen_model_text_generation")
model_text_to_speech = os.getenv("chosen_model_text_to_speech")


model = "gpt-3.5-turbo"
role = "assistant"
personality = "hilarious"
number_of_word = 8
note = "do not repeat the sentence, make your message random"

openai_engine = OpenaiAPI(
    api_key, model_speech_to_text, model_text_generation, model_text_to_speech
)


router = APIRouter()


@router.post("/get_ai_response/")
async def get_ai_response(percentage_done: Item):
    try:
        prompt = (
            f"You are a {personality} assistant. "
            + f" Your response is a {number_of_word}-word sentence"
            + f" to inspire somebody who just got {percentage_done}% of the work done."
            + f"{note}"
        )

        ai_response = openai_engine.request_openai_response_for_todotoday(
            role=role, prompt=prompt
        )

        return {"ai_response": ai_response}
    except Exception as e:
        raise CustomException(e, sys)
