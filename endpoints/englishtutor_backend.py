# _______ BACKEND FOR ENGLISH TUTOR MOBILE _______ #

import sys, os, json
from dotenv import load_dotenv
from fastapi import HTTPException, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi import APIRouter
from pydantic import BaseModel

# ________________ HANDLE THE PATH THING ________________ #
# get the absolute path of the script's directory
script_path = os.path.dirname(os.path.abspath(__file__))
# get the parent directory of the script's directory
parent_path = os.path.dirname(script_path)
sys.path.append(parent_path)


from aiengine.openai_requests import OpenaiAPI
from database.database_handler import PromptHandling
from database.utils import *
from exception import CustomException


# retrieve the text input from the frontend
class TextInput(BaseModel):
    text: str


# ________________ PROMPT HANDLING ________________ #
SERVICE_NAME = "EnglishTutor"

role = "user"
name = "Miss PunsAlot"
gender = "female"
personality = "professional"
position = "English tutor."
note = "Keep responses under 25 words and only in English. Your tutoring is tailored to IELTS speaking practices. "

temporary_prompt_data_file_name = "temporary_prompt_data_englishtutor.json"
prompt_data_file_name = "prompt_data_englishtutor.json"

prompt_handler = PromptHandling(
    role=role,
    name=name,
    gender=gender,
    personality=personality,
    position=position,
    note=note,
    temporary_data_file_name=temporary_prompt_data_file_name,
    data_file_name=prompt_data_file_name,
)
# ------------------------------------------------------------------- #


# ________________ CONFIG OPENAI API ________________ #
load_dotenv()
api_key = os.getenv("OPENAI_THE_HAPPY_CAVE_ENGLISHTUTOR")
model_speech_to_text = os.getenv("chosen_model_speech_to_text")
model_text_generation = os.getenv("chosen_model_text_generation")
model_text_to_speech = os.getenv("chosen_model_text_to_speech")
voice_nova = os.getenv("VOICE_NOVA")

openai_engine = OpenaiAPI(
    api_key, model_speech_to_text, model_text_generation, model_text_to_speech
)
# ------------------------------------------------------------------- #


router = APIRouter()


# _______ HANDLING AI RESPONSE _______ #


# Handle the reset button at the frontend
@router.get("/reset_conversation/")
async def reset_temporary():
    prompt_handler.reset_temporary_prompt_messages()

    return {"response": "conversation reset"}


# Handle post chosen messages to Firestore and Firebase storage and save them
@router.post("/post_messages/")
async def post_user_audio_and_text(
    audio_file: UploadFile = File(...),
    ID: str = Form(...),
    source: str = Form(...),
    time: str = Form(...),
    date: str = Form(...),
    text: str = Form(...),
    userUID: str = Form(...),
):
    try:

        file_url = await upload_messages_to_firebase(
            SERVICE_NAME, audio_file, ID, source, time, date, text, userUID
        )
        return {
            "message": "File and metadata uploaded successfully",
            "file_url": file_url,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process the request: {str(e)}"
        )


# Request ai audio response and send to frontend
@router.post("/get_ai_audio_response/")
async def get_ai_response(input: TextInput):

    try:

        messages = prompt_handler.make_prompt_messages(prompt_input=input.text)

        # Make ai response
        ai_response = openai_engine.request_openai_text_generation(messages=messages)

        # Ensure output
        if not ai_response:
            raise HTTPException(status_code=400, detail="Failed to get ai_response")

        # Store all messages
        prompt_handler.store_prompt_messages(input.text, ai_response)

        # Convert openai response to speech
        audio_output = openai_engine.convert_text_to_speech(voice_nova, ai_response)

        # Ensure output
        if not audio_output:
            raise HTTPException(status_code=400, detail="Failed to get audio_output")

        # Create a generator that yields chunks of data
        def iterfile():
            yield audio_output

        # Use for Post: Return output audio
        return StreamingResponse(iterfile(), media_type="application/octet-stream")

    except Exception as e:
        raise CustomException(e, sys)


# Retrieve ai text response and send to frontend
@router.get("/get_ai_text_response/")
async def get_ai_text_response():

    try:
        path_to_text_data = os.path.join(
            parent_path, "database", "datastorage", prompt_data_file_name
        )

        with open(path_to_text_data, "r") as file:
            data = json.load(file)

        last_ai_text = None
        for entry in reversed(data):
            if entry["role"] == "system":
                last_ai_text = entry["content"]
                break

        if last_ai_text is not None:
            return {"text": last_ai_text}
        else:
            print("No AI text response found")
            return {"text": "No AI text response found"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
