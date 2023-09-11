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
from dalle_utils import generate_image, parse_dalle_command
from chatgpt_utils import process_activity 
from slack_utils import get_thread_starter_user_id


from jira_utils import get_issues_assigned_to_current_user

from UTILITIES.slack_to_chatgpt_payload_parser import user_prompt_papertrail

import chat_with_itself

# default number of conversation rounds
GLOBAL_CONVO_ROUNDS = 2
GLOBAL_STARTER_MESSAGE ="Please tell me a very short story about Seattle in 5 sentences or less."


# load environment variables from .env file
load_dotenv('../../.env')

VERBOSE_MODE = False  # Set to True for verbose output to slack showing json

app = Flask(__name__)
slack_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_token)
bot_adapter = Adapter(Bot(client))

#set vars for things we could track to not duplicate later
bot_user_id = client.auth_test()["user_id"]
bot_initiated_threads = []

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

def handle_history(event, channel_id, thread_ts):
    thread_history = client.conversations_replies(
        channel=channel_id, ts=str(thread_ts), limit=100)['messages']
    user_prompts = user_prompt_papertrail(thread_history)
    client.chat_postMessage(
        channel=channel_id, thread_ts=thread_ts, text=f"User Prompts Papertrail:\n{user_prompts}")
    print("SENDING SLACK AN HTTP200 AFTER POSTING PAPERTRAIL...")

def handle_dalle(event, channel_id, event_text_blocks):
    print(f"USER INVOKED DALLE, CREATING IMAGE.")
    dalle_command = event_text_blocks.replace("$dalle", "").strip()
    n_images, prompt = parse_dalle_command(dalle_command)
    Thread(target=generate_image, args=(event, channel_id, prompt, n_images, VERBOSE_MODE)).start()

def handle_chatwithitself(event, channel_id, event_text_blocks):
    print(f"USER INVOKED CHATWITHITSELF, STARTING CONVERSATION.")
    convo_rounds = GLOBAL_CONVO_ROUNDS  
    if "--" in event_text_blocks:
        try:
            convo_rounds = int(event_text_blocks.split("--")[1].strip())
        except ValueError:
            pass
    thread_ts = event.get('thread_ts', event.get('ts'))
    Thread(target=chat_with_itself.chat_with_itself,
           args=(client, channel_id, bot_user_id, thread_ts, GLOBAL_STARTER_MESSAGE, convo_rounds)).start()

def handle_jira(event, channel_id, event_text_blocks):
    if "$jira --query" in event_text_blocks:
        print(f"USER INVOKED JIRA, FETCHING ISSUES.")
        issues = get_issues_assigned_to_current_user(payload=event_text_blocks)
        Thread(target=client.chat_postMessage, kwargs={
            "channel": channel_id,
            "blocks": issues['blocks'],
            "text": "Here are your current issues in JIRA:",
            "thread_ts": event.get('thread_ts', event.get('ts'))
        }).start()

def react_to_message(event, channel_id):
    timestamp = event.get('ts')
    try:
        client.reactions_add(name='hourglass', channel=channel_id, timestamp=timestamp)
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")

def default_handler(event, channel_id, thread_ts):
    print(f"USER INVOKED BOT, REPLYING TO USER VIA CHATGPT.")
    if (event.get('type') == 'app_mention') or ("@bot" in event.get('text', '').lower()) or (event.get('type') == "app_mention"):
        Thread(target=process_activity, args=(event, VERBOSE_MODE)).start() 

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.get_json()
    print(f"HERE IS THE PAYLOAD SLACK_EVENTS IS PROCESSSING: {data}")

    if "challenge" in data:
        return make_response(data["challenge"], 200, {"content_type": "application/json"})

    event = data.get('event', {})
    event_type = event.get('type')

    if event_type == 'reaction_added':
        return make_response("", 200)

    elif event_type == 'message':
        channel_id = event['channel']
        thread_ts = event.get('thread_ts')
        event_text_blocks = message_from_blocks(event).lower()
        print(f"EVENT TEXT BLOCKS: {event_text_blocks}")

        if event.get('subtype') == 'bot_message' or event.get('user') == bot_user_id:
            return make_response("Ignore bot message", 200)

        if event.get('type') == 'message':
            react_to_message(event, channel_id)

        if "$history" in event_text_blocks:
            handle_history(event, channel_id, thread_ts)

        elif "$dalle" in event_text_blocks:
            handle_dalle(event, channel_id, event_text_blocks)

        elif "$chatwithitself" in event_text_blocks:
            handle_chatwithitself(event, channel_id, event_text_blocks)

        elif "$jira --query" in event_text_blocks:
            handle_jira(event, channel_id, event_text_blocks)

        else:
            default_handler(event, channel_id, thread_ts)

        print("SENDING SLACK AN HTTP200 SO WE CAN CONTINUE PROCESSING...")
        return make_response("", 200)

    elif event_type == 'app_mention':
        channel_id = event['channel']
        thread_ts = event.get('thread_ts')
        default_handler(event, channel_id, thread_ts)
        print("SENDING SLACK AN HTTP200 SO WE CAN CONTINUE PROCESSING...")
        return make_response("", 200)

    else:
        print(f'Unhandled event type: {event_type}')
        return make_response("Unhandled event or message type", 400)

if __name__ == "__main__":
    app.run(port=int(os.getenv('PORT', 3000)))