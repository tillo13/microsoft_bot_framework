from botbuilder.core import TurnContext
from botbuilder.schema import Activity
import requests
import json
import os
from datetime import timezone
import datetime
from UTILITIES.slack_to_chatgpt_payload_parser import slack_to_chatgpt_parser

class Bot:
    def __init__(self, client):
        self.client = client

    def on_turn(self, context: TurnContext):
        message_content, details, entire_json_payload, usage = self.talk_to_chatbot(context.activity)  # add usage here
        context.activity.text = message_content
        context.activity.bot_responses = {"message_content": message_content, "details": details, "entire_json_payload": entire_json_payload, 'usage': usage}  # add usage here
        return context.activity

    def talk_to_chatbot(self, activity: Activity):
            headers = { 'api-key': os.getenv('OPENAI_API_KEY') }
            
            channel_id = activity.conversation.id
            thread_ts = activity.timestamp
            
            # If 'thread_ts' is not None, then it's a threaded message and we fetch the conversation history. 
            # If it is None, then the 'initial_message' will contain only one message which was directed at the bot.
            if thread_ts is not None:
                print(f"CURRENT THREAD_TS in def talk_to_chatbot: {thread_ts}")

                unix_ts_of_current_thread = thread_ts.replace(tzinfo=timezone.utc).timestamp()
                print(f"Converted thread_ts in Unix timestamp format: {unix_ts_of_current_thread}")

                response = self.client.conversations_replies(  
                    channel=channel_id, 
                    ts=str(unix_ts_of_current_thread), 
                    limit=100 
                )

                print(f"Calling Slack conversations_replies API with channel_id: {channel_id}, thread_ts: {thread_ts}")
                print(f"RESPONSE FROM CONVERSATION ENDPOINT: {response}")

                # Below is the conversation history
                thread_history = response['messages']  

                initial_message = slack_to_chatgpt_parser(thread_history)
            else:
                # If there's no thread history (i.e., when 'thread_ts' is None), 
                # then the list 'initial_message' will contain only the one new message from the current user interaction.
                initial_message = [{'role': 'user', 'content': activity.text}]

            data = { "messages": initial_message }

            url = f'{os.getenv("OPENAI_API_BASE_URL")}/{os.getenv("OPENAI_API_DEPLOYMENT")}?api-version={os.getenv("OPENAI_API_VERSION")}'

            #tell the terminal 
            print("OPENAI PAYLOAD BEFORE SENDING:" + json.dumps(data, indent=2))
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                result = response.json()
                print(result)  # print to see the structure
                
                # Print the total token usage from the response
                total_tokens = result.get('usage', {}).get('total_tokens')                
                print(f'Total token usage in bot_logic.py: {total_tokens}')

                message_content = result['choices'][0]['message']['content']
                details = "OpenAI response details:"
                
                for k, v in result.items():
                    if k != 'choices':
                        if isinstance(v, dict):
                            for nested_k, nested_v in v.items():
                                details += f"{nested_k}: {nested_v}"
                        else:
                            details += f"{k}: {v}"

                entire_json_payload = f"Entire current JSON payload:{json.dumps(result, indent=2)}"  

                return message_content, details, entire_json_payload, result['usage']


            else:
                return {"message_content": 'An error occurred while communicating with the bot.', "details": '', "entire_json_payload": '', 'usage': {}} 