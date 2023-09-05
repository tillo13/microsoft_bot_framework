from botbuilder.core import TurnContext
from botbuilder.schema import Activity
import requests
import json
import os
from datetime import timezone
import datetime


class Bot:
    def __init__(self, client):
        self.client = client

    def on_turn(self, context: TurnContext):
        message_content, details, entire_json_payload = self.talk_to_chatbot(context.activity)
        context.activity.text = message_content
        context.activity.bot_responses = {"message_content": message_content, "details": details, "entire_json_payload": entire_json_payload}
        return context.activity

    def talk_to_chatbot(self, activity: Activity):
        headers = { 'api-key': os.getenv('OPENAI_API_KEY') }
        
        channel_id = activity.conversation.id
        thread_ts = activity.timestamp

        messages = [{'role': 'system', 'content': 'You are a kind, attentive assistant who always looks at specific details from this exact thread conversation and provide accurate responses by referencing exact names, dates, times, and key information from those conversations if available first, prior to hallucinating any answers.'}]
        
        # Check if thread_ts is None
        if thread_ts is None:
            messages.append({'role': 'user', 'content': activity.text})
        else:
            print(f"CURRENT THREAD_TS in def talk_to_chatbot: {thread_ts}")

            # Convert thread_ts (standard format) back to Unix timestamp to pass to slack
            unix_ts_of_current_thread = thread_ts.replace(tzinfo=timezone.utc).timestamp()
            print(f"Converted thread_ts in Unix timestamp format: {unix_ts_of_current_thread}")

            response = self.client.conversations_replies(
                channel=channel_id,
                ts=str(unix_ts_of_current_thread),
                #ts="1693869882.640909", #uncomment this to test as we know this payload works

                limit=100 # Get the last 100 messages in the slack thread
            )
            print(f"Calling Slack conversations_replies API with channel_id: {channel_id}, thread_ts: {thread_ts}")
            print(f"RESPONSE FROM CONVERSATION ENDPOINT: {response}")

            thread_history = response['messages']
            for message in thread_history:
                if message['type'] == 'message' and 'bot_id' not in message: # Exclude bot messages
                    messages.append({'role': 'user', 'content': message['text']})
            
        data = { "messages": messages }

        url = f'{os.getenv("OPENAI_API_BASE_URL")}/{os.getenv("OPENAI_API_DEPLOYMENT")}?api-version={os.getenv("OPENAI_API_VERSION")}'

        #tell the terminal 
        print("OPENAI PAYLOAD BEFORE SENDING:" + json.dumps(data, indent=2))
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            print(result)  # print to see the structure
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

            return message_content, details, entire_json_payload


        else:
            return {"message_content": 'An error occurred while communicating with the bot.', "details": '', "entire_json_payload": ''} 