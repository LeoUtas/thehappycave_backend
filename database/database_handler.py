import os, sys, json


# ________________ HANDLE THE PATH THING ________________ #
# get the absolute path of the script's directory
script_path = os.path.dirname(os.path.abspath(__file__))
# get the parent directory of the script's directory
parent_path = os.path.dirname(script_path)
sys.path.append(parent_path)
from exception import CustomException


class PromptHandling:

    def __init__(
        self,
        role,
        name,
        gender,
        personality,
        position,
        note,
        temporary_data_file_name,
        data_file_name,
    ):
        self.role = role
        self.name = name
        self.gender = gender
        self.personality = personality
        self.position = position
        self.note = note

        self.data_path = os.path.join(
            parent_path, "database", "datastorage", data_file_name
        )

        self.temporary_data_path = os.path.join(
            parent_path, "database", "datastorage", temporary_data_file_name
        )

    # ________________ MAKE INIT PROMPT ________________ #
    def make_init_prompt(self):
        try:
            init_prompt = (
                f"Your name is {self.name}. "
                + f"You are a {self.gender}"
                + f" {self.personality}"
                + f" {self.position}"
                + f" {self.note} "
            )

            return init_prompt

        except Exception as e:
            raise CustomException(e, sys)

    # ________________ GET RECENT PROMPT MESSAGES ________________ #
    def get_recent_messages(
        self, limit: bool = True, number_of_recent_messages: int = 6
    ):

        init_instruction = {
            "role": "user",
            "content": self.make_init_prompt(),
        }

        # Initialize messages
        messages = []

        # Append init_instruction to message
        messages.append(init_instruction)

        try:
            with open(self.data_path) as file:
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

            with open(self.temporary_data_path, "w") as file:
                json.dump(messages, file)

        except:
            pass

        # Return messages
        return messages

    # ________________ SAVE ALL THE MESSAGES ________________ #
    def store_messages(self, request_message, response_message):

        try:

            # Check if the file exists and has content
            if os.path.exists(self.data_path) and os.path.getsize(self.data_path) > 0:
                with open(self.data_path, "r") as file:
                    messages = json.load(file)
            else:
                messages = []

            # Add messages to data
            user_message = {"role": "user", "content": request_message}
            system_message = {"role": "system", "content": response_message}
            messages.append(user_message)
            messages.append(system_message)

            # Save the updated file
            with open(self.data_path, "w") as file:
                json.dump(messages, file)

        except Exception as e:
            raise CustomException(e, sys)

    def make_promptmessages(self, prompt_input: str):
        try:

            messages = self.get_recent_messages()

            user_messages = {
                "role": "user",
                "content": prompt_input,
            }

            messages.append(user_messages)

            return messages

        except Exception as e:
            raise CustomException(e, sys)

    # ________________ RESET THE TEMPORARY DATA FILE ________________ #
    def reset_temporary_messages(self):

        # Write an empty file
        open(self.temporary_data_path, "w")
