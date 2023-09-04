from botbuilder.core import TurnContext
from botbuilder.schema import Activity
import requests
import json
import os

class Bot:
    def __init__(self):
        self.sessions = {}

    def on_turn(self, context: TurnContext):
        self.record_sessions(context.activity)
        context.activity.bot_responses = self.talk_to_chatbot(context.activity)

    def record_sessions(self, activity: Activity):
        conv_id = activity.conversation.id
        if not conv_id in self.sessions:
            self.sessions[conv_id] = []
        self.sessions[conv_id].append(activity.text)

    def talk_to_chatbot(self, activity: Activity):
        headers = {
            'api-key': os.getenv('OPENAI_API_KEY')
        }

        data = {
            "messages": [{
                "role": "system",
                "content": "You are a helpful assistant."
            }, {
                "role": "user",
                "content": activity.text
            }]
        }

        url = f'{os.getenv("OPENAI_API_BASE_URL")}/{os.getenv("OPENAI_API_DEPLOYMENT")}?api-version={os.getenv("OPENAI_API_VERSION")}'

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            print(result)  # print to see the structure
            message_content = result['choices'][0]['message']['content']
            details = "OpenAI response details:\n____\n"
            
            for k, v in result.items():
                if k != 'choices':
                    if isinstance(v, dict):
                        for nested_k, nested_v in v.items():
                            details += f"{nested_k}: {nested_v}\n"
                    else:
                        details += f"{k}: {v}\n"

            entire_json_payload = f"Entire current JSON payload:\n____\n{json.dumps(result, indent=2)}"  # Add this line

            return {"message_content": message_content, "details": details, "entire_json_payload": entire_json_payload}

        else:
            return {"message_content": 'An error occurred while communicating with the bot.', "details": '', "entire_json_payload": ''} 