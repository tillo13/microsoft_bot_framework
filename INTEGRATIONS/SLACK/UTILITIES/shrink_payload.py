import re

def remove_extra_spaces_comments(text):
    lines = text.split('\n')
    stripped = [line for line in lines if not line.strip().startswith('#')]
    clean_text = ' '.join(stripped)
    clean_text = re.sub('\s+', ' ', clean_text).strip()  
    clean_text = re.sub('\"\"\"(.*?)\"\"\"', '', clean_text, flags=re.MULTILINE|re.DOTALL) # remove multi-line comments
    clean_text = re.sub("'''(.*?)'''", '', clean_text, flags=re.MULTILINE|re.DOTALL) # remove multi-line comments
    return clean_text
code = """



slack_events_listener.py
from dotenv import load_dotenv
from flask import Flask, request, make_response
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import json
from bot_logic import Bot
from bot_adapter import Adapter
from botbuilder.schema import Activity
from threading import Thread
from datetime import datetime



# load environment variables from .env file
load_dotenv('../../.env')

VERBOSE_MODE = False  # Set to True for verbose output to slack showing json

app = Flask(__name__)
slack_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_token)
bot_adapter = Adapter(Bot(client))

bot_user_id = client.auth_test()["user_id"]
#this is to tell a comparision if the bot has replied to an initial request
bot_initiated_threads = []

def get_thread_starter_user_id(channel, thread_ts):
    response = client.conversations_replies(channel=channel, ts=thread_ts)
    starter_message = response['messages'][0]
    starter_user_id = starter_message['user']

    if starter_user_id == bot_user_id and thread_ts not in bot_initiated_threads:
        bot_initiated_threads.append(thread_ts)
        
    return starter_user_id

# initialize empty lists in the global scope
bot_replied_to_messages_ts = []

def message_from_blocks(event):
    blocks = event.get('blocks', [])
    message_text = ""
    for block in blocks:
        elements = block.get('elements', [])
        for element in elements:
            element_list = element.get('elements', [])
            for item in element_list:
                if item.get('type') == 'text':
                    message_text += item.get('text', '')
                elif item.get('type') == 'user' and item.get('user_id') == bot_user_id:
                    message_text += f"<@{bot_user_id}>"
    return message_text

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.get_json()

    if "challenge" in data:
        return make_response(data["challenge"], 200, {"content_type": "application/json"})

    if "event" in data:
        event = data["event"]

        # Ignore bot's own message
        if event.get("subtype") == "bot_message" or event.get("bot_profile") is not None:
            return make_response("Ignore bot message", 200)

        event_text_blocks = message_from_blocks(event).lower()
        thread_ts = event.get('thread_ts')

        if thread_ts and event['user'] != bot_user_id:
            print(f"THREADED CHATGPT MESSAGE, INVOKING {bot_user_id} BOT.")
            process_activity(event)
        else:
            if (event.get('type') == 'app_mention') or ("@bot" in event_text_blocks):
                print(f"USER INVOKED BOT, REPLYING TO USER VIA CHATGPT.")
                process_activity(event)
            else:
                print("USER USED SLACK, BUT DID NOT CALL BOT.")

    return make_response("", 200)

def process_activity(event):
    channel_id = event['channel']
    thread_ts = event.get('thread_ts')

    # Convert thread_ts to datetime object
    if thread_ts is not None:
        # Slack's timestamp is in seconds, need to convert it to a datetime object
        timestamp = datetime.utcfromtimestamp(float(thread_ts))
    else:
        timestamp = None

    activity = {
        "type": "message",
        "text": event["text"],
        "channelId": "slack",
        "conversation": {"id": channel_id,},
        "from": {"id": event.get("user_id")},
        "timestamp": timestamp, # set the timestamp attribute
    }

    message_activity = Activity().deserialize(activity)
    bot_adapter.process_activity(message_activity)

    send_message(
        event["channel"],
        event["ts"],
        message_activity.bot_responses['message_content'],
        message_activity.bot_responses['details'],
        message_activity.bot_responses['entire_json_payload']
    )

def send_message(channel, thread_ts, bot_message, response_json, entire_json_payload):
    # Format response
    formatted_response_str = json.dumps(response_json, indent=2)

    # First define your message_block
    message_block = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": bot_message
                }
            }
    ]

    if VERBOSE_MODE:
        message_block += [
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{formatted_response_str}```",                
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{entire_json_payload}```",                
                }
            }
        ]

    # Now, send the client.chat_postMessage containing your message_block
    client.chat_postMessage(channel=channel, thread_ts=thread_ts,
                            text="A placeholder message titled test123.", blocks=message_block)

if __name__ == "__main__":
    app.run(port=int(os.getenv('PORT', 3000)))







bot_logic.py:
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






    bot_adapter.py: 
    from botbuilder.core import BotAdapter, TurnContext

class Adapter(BotAdapter):
    def __init__(self, bot):
        self.bot = bot

    def send_activities(self, context: TurnContext, activities):
        return [0] * len(activities)

    def update_activity(self, context, activity):
        pass

    def delete_activity(self, context, reference):
        pass

    def process_activity(self, activity):
        turn_context = TurnContext(self, activity)
        return self.run_pipeline(self.bot.on_turn(turn_context))

        
        
        """
clean_code = remove_extra_spaces_comments(code)
print(clean_code)