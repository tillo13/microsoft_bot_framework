from botbuilder.core import TurnContext
from botbuilder.schema import Activity
import requests
import json
import re
import os
from datetime import timezone
import datetime
from UTILITIES.slack_to_chatgpt_payload_parser import slack_to_chatgpt_parser,user_prompt_papertrail

def phrase_to_requery_for(message_content: str):
    # Define patterns to match against
    patterns = [
        "as an ai",
        "access to personal information",
        "I do not have access to previous conversations",
        "I don't have access to information shared in previous conversations",
        "I don't have information about",
        "I don't have access to information about",
        # More patterns...
    ]

    # Check if any pattern is found in the message content
    for pattern in patterns:
        if re.search(pattern, message_content.lower()):
            return True
    
    return False

class Bot:
    def __init__(self, client):
        self.client = client

    @staticmethod
    def clean_openai_json(payload):
        for item in payload["messages"]:
            if item["role"] == "assistant" and "as an ai" in item["content"].lower():
                item["content"] = "Let me look at the previous conversations"
        return payload
    
    def add_papertrail_to_conv(self, activity: Activity):
        headers = { 'api-key': os.getenv('OPENAI_API_KEY') }
        channel_id = activity.conversation.id
        thread_ts = activity.timestamp
        if thread_ts is not None:
            unix_ts_of_current_thread = thread_ts.replace(tzinfo=timezone.utc).timestamp()
    
            response = self.client.conversations_replies(  
                channel=channel_id, 
                ts=str(unix_ts_of_current_thread), 
                limit=100 
            )
            thread_history = response['messages']  
            user_prompts = user_prompt_papertrail(thread_history)

            data = { "messages": [{"role": "assistant", "content": f"Please process these past user messages:\n{user_prompts}"}] }

            data = self.clean_openai_json(data)
            url = f'{os.getenv("OPENAI_API_BASE_URL")}/{os.getenv("OPENAI_API_DEPLOYMENT")}?api-version={os.getenv("OPENAI_API_VERSION")}'
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                message_content = result['choices'][0]['message']['content']
                return message_content
            else:
                return "An error occurred while communicating with the bot."
        else:
            return "This feature works in a thread. Please use $memory command in a thread."





    def on_turn(self, context: TurnContext):
        if '$memory' in context.activity.text:
            message_content = self.add_papertrail_to_conv(context.activity)
            context.activity.bot_responses = {
                "message_content": message_content,
                "details": '',  # Add an empty string or suitable message
                "entire_json_payload": '',  # Add an empty string or suitable data
                "usage": {}  # Add a suitable dictionary
            }
        else:
            message_content, details, entire_json_payload, usage = self.talk_to_chatbot(context.activity)
            context.activity.text = message_content
            context.activity.bot_responses = {"message_content": message_content, "details": details, "entire_json_payload": entire_json_payload, 'usage': usage}
        return context.activity
        
    def talk_to_chatbot(self, activity: Activity):
            headers = { 'api-key': os.getenv('OPENAI_API_KEY') }
            
            channel_id = activity.conversation.id
            thread_ts = activity.timestamp
            
            if thread_ts is not None:
                unix_ts_of_current_thread = thread_ts.replace(tzinfo=timezone.utc).timestamp()

                response = self.client.conversations_replies(  
                    channel=channel_id, 
                    ts=str(unix_ts_of_current_thread), 
                    limit=100 
                )

                thread_history = response['messages']  
                initial_message = slack_to_chatgpt_parser(thread_history)
            else:
                initial_message = [{'role': 'user', 'content': activity.text}]

            data = { "messages": initial_message }
            data = self.clean_openai_json(data)

            url = f'{os.getenv("OPENAI_API_BASE_URL")}/{os.getenv("OPENAI_API_DEPLOYMENT")}?api-version={os.getenv("OPENAI_API_VERSION")}'
            RETRY_ATTEMPTS = 5  
            retry_counter = 0
            thread_ts = activity.timestamp
            
            retry_chat_history = False # New flag for managing chat history retries

            while retry_counter < RETRY_ATTEMPTS:

                def check_message(message_content):
                    return phrase_to_requery_for(message_content)

                response = requests.post(url, headers=headers, json=data)

                if response.status_code == 200:
                    result = response.json()
                    message_content = result['choices'][0]['message']['content']

                    if check_message(message_content):
                        if not retry_chat_history: # Only retry with chat history once
                            retry_counter += 1
                            retry_chat_history = True
                            thread_ts_unix = thread_ts.replace(tzinfo=timezone.utc).timestamp()
                            thread_ts_str2 = str(thread_ts_unix)
                            self.client.chat_postMessage(channel=channel_id, thread_ts=thread_ts_str2, text="One moment while I dig into our convo a bit more...")
                            thread_history = self.client.conversations_replies(channel=channel_id, ts=thread_ts_str2, limit=100)['messages']
                            user_prompts = user_prompt_papertrail(thread_history)
        
                            data['messages'].append({"role": "assistant", "content": "It appears I am not recalling the entire conversation. Can you reply with everything you've said to this point?"})
                            data['messages'].append({"role": "user", "content": user_prompts})
                            continue
                        else: # If it still triggers after retrying with chat history
                            break
                    elif response.status_code != 200: # logic for status code != 200 remains the same
                        retry_counter += 1
                    else: # If the response is acceptable, break the loop
                        break

            if retry_counter == RETRY_ATTEMPTS:
                result = {"choices": [{"message": {"content": "I'm sorry, but I'm unable to recall the answer. Could you please ask again?"}}]}
                message_content = result['choices'][0]['message']['content']
                details = "Exhausted retries and still did not find the relevant answer in the user conversation history."
                entire_json_payload = "Not applicable in this case."
                usage = {}  # Since there's no usage data when retries are exhausted

            # If retries are exhausted, add the bot's last response to the payload
            if retry_counter == RETRY_ATTEMPTS:
                data['messages'].append({"role": "assistant","content": "I'm sorry, but I'm unable to recall the answer. Could you please ask again?"})

            #tell the terminal 
            print("OPENAI PAYLOAD BEFORE SENDING:" + json.dumps(data, indent=2))   

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                result = response.json()
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

            return {"message_content": 'An error occurred while communicating with the bot.', "details": '', "entire_json_payload": '', 'usage': {}}