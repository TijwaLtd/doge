import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize Grok client
XAI_API_KEY = os.getenv("XAI_API_KEY")
print(XAI_API_KEY)

class GrokAPI:
    def __init__(self):
        self.client = OpenAI(
            api_key=XAI_API_KEY,
            base_url="https://api.x.ai/v1",
        )

    def validate_and_fill_form(self, form_data):
        """
        Sends form data to Grok for validation and auto-fill.
        :param form_data: Dictionary containing form fields (name, email, etc.)
        :return: Validated and auto-filled form data or error message
        """
        try:
            user_message = f"Validate and complete this tax form: {form_data}"

            completion = self.client.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": "If any fields are missing or incorrect, provide recommended values to auto-fill the form."},
                    {"role": "user", "content": user_message},
                ],
            )

            raw_response = completion.choices[0].message.content

            try:
                import json
                response = json.loads(raw_response)
            except json.JSONDecodeError:
                response = {"message": raw_response}

            return response
        except Exception as e:
            return {"error": str(e)}

