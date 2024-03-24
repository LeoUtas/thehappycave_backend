# _______ BACKEND FOR BIRDCLASSIFICATION _______ #

import sys, os
from dotenv import load_dotenv, find_dotenv, set_key
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
    species: str


# ________________ CONFIG OPENAI API ________________ #
load_dotenv(override=True)
api_key = os.getenv("BIRD_CLASSIFICATION_API_KEY")
model_speech_to_text = os.getenv("chosen_model_speech_to_text")
model_text_generation = os.getenv("chosen_model_text_generation")
model_text_to_speech = os.getenv("chosen_model_text_to_speech")


role = "assistant"
personality = "professional"
note = ""

openai_engine = OpenaiAPI(
    api_key, model_speech_to_text, model_text_generation, model_text_to_speech
)


router = APIRouter()


@router.post("/get_ai_response/")
async def get_ai_response(item: Item):
    try:

        species = item.species

        prompt = (
            f"You are a {personality} zoologist, "
            + f"telling a fun fact about a bird species, {species}."
            + f"{note}"
        )

        ai_response = openai_engine.request_openai_response_for_funfact(
            role=role, prompt=prompt
        )

        return {"ai_response": ai_response}

    except Exception as e:
        raise CustomException(e, sys)


# if __name__ == "__main__":
#     get_ai_response("ga")
