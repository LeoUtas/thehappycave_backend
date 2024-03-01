import os, sys, json


# ________________ HANDLE THE PATH THING ________________ #
# get the absolute path of the script's directory
script_path = os.path.dirname(os.path.abspath(__file__))
# get the parent directory of the script's directory
parent_path = os.path.dirname(script_path)
sys.path.append(parent_path)
from dotenv import load_dotenv
from exception import CustomException


# ________________ PROMPT ENGINEERING ________________ #
load_dotenv()
name = os.getenv("name")
gender = os.getenv("gender")
personality = os.getenv("personality")
position = os.getenv("position")
note = os.getenv("note")

temporary_data_file_name = "temporary_data.json"
data_file_name = "data.json"


# ________________ MAKE INIT PROMPT ________________ #
def make_init_prompt():
    try:
        init_prompt = (
            f"Your name is {name}. "
            + f"You are a {gender}"
            + f" {personality}"
            + f" {position}"
            + f" {note} "
        )

        return init_prompt

    except Exception as e:
        raise CustomException(e, sys)


# ________________ GET RECENT PROMPT MESSAGES ________________ #
def get_recent_messages(limit: bool = True, number_of_recent_messages: int = 5):

    data_path = os.path.join(parent_path, "database", data_file_name)
    temporary_data_path = os.path.join(
        parent_path, "database", temporary_data_file_name
    )

    init_instruction = {
        "role": "user",
        "content": make_init_prompt(),
    }

    # Initialize messages
    messages = []

    # Append init_instruction to message
    messages.append(init_instruction)

    try:
        with open(data_path) as file:
            data = json.load(file)

            if limit == True:

                if data:
                    if len(data) < number_of_recent_messages:
                        for item in data:
                            messages.append(item)
                    else:
                        for item in data[-number_of_recent_messages:]:
                            messages.append(item)

            else:

                for item in data:
                    messages.append(item)

        with open(temporary_data_path, "w") as file:
            json.dump(messages, file)

    except:
        pass

    # Return messages
    return messages


# ________________ SAVE ALL THE MESSAGES ________________ #
def store_messages(request_message, response_message):

    try:
        data_path = os.path.join(parent_path, "database", data_file_name)

        # Check if the file exists and has content
        if os.path.exists(data_path) and os.path.getsize(data_path) > 0:
            with open(data_path, "r") as file:
                messages = json.load(file)
        else:
            messages = []

        # Add messages to data
        user_message = {"role": "user", "content": request_message}
        system_message = {"role": "system", "content": response_message}
        messages.append(user_message)
        messages.append(system_message)

        # Save the updated file
        with open(data_path, "w") as file:
            json.dump(messages, file)

    except Exception as e:
        raise CustomException(e, sys)


# ________________ RESET THE TEMPORARY DATA FILE ________________ #
def reset_temporary_messages(temporary_data_path):

    temporary_data_path = os.path.join(
        parent_path, "database", temporary_data_file_name
    )

    # Write an empty file
    open(temporary_data_path, "w")
