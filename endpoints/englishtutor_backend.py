# _______ BACKEND FOR ENGLISH TUTOR MOBILE _______ #

import sys, os, json
from datetime import datetime
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
from aiengine.the11labs_requests import The11Labs
from aiengine.mistralai_requests import *
from database.database_handler import PromptHandling
from database.utils import upload_messages_to_firebase
from exception import CustomException


# retrieve the text input from the frontend
class TextInput(BaseModel):
    text: str


# ________________ PROMPT HANDLING ________________ #
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
model_speech_to_text = os.getenv("chosen_model_speech_to_text")
model_text_generation = os.getenv("chosen_model_text_generation")
model_text_to_speech = os.getenv("chosen_model_text_to_speech")
voice_nova = os.getenv("VOICE_NOVA")

openai_engine = OpenaiAPI(
    model_speech_to_text, model_text_generation, model_text_to_speech
)
the11labs_engine = The11Labs()
# ------------------------------------------------------------------- #


router = APIRouter()


# _______ HANDLING AI RESPONSE _______ #
@router.get("/reset_conversation/")
async def reset_temporary():
    prompt_handler.reset_temporary_prompt_messages()

    return {"response": "conversation reset"}


@router.post("/post_messages/")
async def post_user_audio_and_text(
    audio_file: UploadFile = File(...),
    ID: str = Form(...),
    source: str = Form(...),
    date: str = Form(...),
    text: str = Form(...),
    userUID: str = Form(...),
):
    try:

        file_url = await upload_messages_to_firebase(
            audio_file, ID, source, date, text, userUID
        )
        return {
            "message": "File and metadata uploaded successfully",
            "file_url": file_url,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process the request: {str(e)}"
        )


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

        # # Ensure the directory exists
        # path = os.path.join(parent_path, "database", "openai_audio")
        # os.makedirs(path, exist_ok=True)

        # # Construct a unique file name
        # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # file_name = f"openai_{timestamp}.mp3"
        # file_path = os.path.join(path, file_name)

        # # Save the audio_output to a file
        # with open(file_path, "wb") as file:
        #     file.write(audio_output)

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


@router.get("/get_ai_text_response/")
async def get_ai_text_response():

    try:
        path_to_text_data = os.path.join(
            parent_path, "database", "datastorage", prompt_data_file_name
        )

        with open(path_to_text_data, "r") as file:
            data = json.load(file)

        last_openai_text = None
        for entry in reversed(data):
            if entry["role"] == "system":
                last_openai_text = entry["content"]
                break

        if last_openai_text is not None:
            return {"text": last_openai_text}
        else:
            print("No AI text response found")
            return {"text": "No AI text response found"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
