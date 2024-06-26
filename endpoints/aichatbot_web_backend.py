# _______ BACKEND FOR AICHATBOT WEB _______ #

import sys, os
from dotenv import load_dotenv
from fastapi import File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi import APIRouter

# ________________ HANDLE THE PATH THING ________________ #
# get the absolute path of the script's directory
script_path = os.path.dirname(os.path.abspath(__file__))
# get the parent directory of the script's directory
parent_path = os.path.dirname(script_path)
sys.path.append(parent_path)


from aiengine.openai_requests import OpenaiAPI
from database.database_handler import PromptHandling
from exception import CustomException


# ________________ PROMPT HANDLING ________________ #
role = "user"
name = "Miss PunsAlot"
gender = "female"
personality = "hilarious"
position = "English tutor."
note = "Keep responses under 15 words and only in English. Your tutoring is tailored to IELTS speaking practices. "

temporary_data_file_name = "temporary_data_aichatbot_web.json"
data_file_name = "data_data_aichatbot_web.json"

prompt_handler = PromptHandling(
    role=role,
    name=name,
    gender=gender,
    personality=personality,
    position=position,
    note=note,
    temporary_data_file_name=temporary_data_file_name,
    data_file_name=data_file_name,
)
# ------------------------------------------------------------------- #


# ________________ CONFIG OPENAI API ________________ #
load_dotenv()
api_key = os.getenv("AICHATBOT_WEB_API_KEY")
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
@router.get("/reset_conversation/")
async def reset_temporary():
    prompt_handler.reset_temporary_messages()

    return {"response": "conversation reset"}


bug_phrases = ["you", "thank you.", "thank you for watching!", "thanks for watching!"]


@router.post("/get_ai_response/")
async def get_ai_response(file: UploadFile = File(...)):
    try:

        # Save the file temporarily
        with open(file.filename, "wb") as buffer:
            buffer.write(file.file.read())
        audio_input = open(file.filename, "rb")

        # Convert audio to text openai engine
        transcript = openai_engine.convert_speech_to_text(audio_input=audio_input)
        print(f"before: {transcript}")
        if transcript.lower().strip() in bug_phrases:
            transcript = "ew"

        print(f"after: {transcript}")
        # Ensure output
        if not transcript:
            raise HTTPException(status_code=400, detail="Failed to get transcript")

        messages = prompt_handler.make_promptmessages(prompt_input=transcript)

        # Make ai response
        ai_response = openai_engine.request_openai_text_generation(messages=messages)

        # Ensure output
        if not ai_response:
            raise HTTPException(status_code=400, detail="Failed to get ai_response")

        # Store all messages
        prompt_handler.store_messages(transcript, ai_response)

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
