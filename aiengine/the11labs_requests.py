import requests, os, sys

# ________________ HANDLE THE PATH THING ________________ #
# get the absolute path of the script's directory
script_path = os.path.dirname(os.path.abspath(__file__))
# get the parent directory of the script's directory
parent_path = os.path.dirname(script_path)
sys.path.append(parent_path)

from dotenv import load_dotenv
from exception import CustomException


load_dotenv()
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
ELEVEN_LABS_CHOSEN_VOICE_KEY = os.getenv("VOICE_RACHEL")


# make 11labs api requests
class The11Labs:
    # ________________ CONVERT TEXT TO SPEECH USING 11LABS ________________ #
    def convert_text_to_speech(self, text_input: str):
        data = {
            "text": text_input,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
        }

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVEN_LABS_API_KEY,
        }

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_LABS_CHOSEN_VOICE_KEY}"

        # Send the requests to 11Labs
        try:
            response = requests.post(url, json=data, headers=headers)

        except Exception as e:
            raise CustomException(e, sys)

        # Handle the responses from 11Labs
        if response.status_code == 200:
            # CHUNK_SIZE = 1024
            # with open("output.mp3", "wb") as f:
            #     for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            #         if chunk:
            #             f.write(chunk)

            return response.content

        else:
            # Handle non-200 responses here
            print(f"Error: {response.status_code} - {response.text}")
            return
