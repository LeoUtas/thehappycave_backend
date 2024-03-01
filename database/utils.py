    def make_messages(prompt_input: str):
        try:

            messages = get_recent_messages()

            user_messages = {
                "role": "user",
                "content": prompt_input,
            }

            messages.append(user_messages)

        except Exception as e:
            raise CustomException(e, sys)