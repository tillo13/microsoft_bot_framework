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
from chatgpt_utils import get_thread_starter_user_id, process_activity 

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

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.get_json()

    # Print the entire request payload in test
    #print(f"HERE IS THE PAYLOAD SLACK_EVENTS IS PROCESSSING: {data}")

    #bot_mention = f"<@{bot_user_id}>"
    if "challenge" in data:
        return make_response(data["challenge"], 200, {"content_type": "application/json"})
    if "event" in data:
        event = data["event"]
        event_type = event.get('type')

        if event_type == 'reaction_added':
            print("EMOJI ADDED")
            return make_response("", 200)

        elif event_type == 'message':

            # Retrieve the channel_id from the event data:
            channel_id = event['channel']

            # Ignore bot's own messages
            if event.get('subtype') == 'bot_message' or event.get('user') == bot_user_id:
                return make_response("Ignore bot message", 200)
            event_text_blocks = message_from_blocks(event).lower()

            # If the event is a message, react with the hourglass emoji  
            if event.get('type') == 'message':
                timestamp = event.get('ts')
                # Send a reaction
                try:
                    client.reactions_add(name='hourglass', channel=channel_id, timestamp=timestamp)
                except SlackApiError as e:
                    print(f"Got an error: {e.response['error']}")

            # Test the event_text_block:
            print(f"Event text blocks: {event_text_blocks}")

            thread_ts = event.get('thread_ts')

            if "$history" in event_text_blocks:
                # Fetch the thread history
                thread_history = client.conversations_replies(
                    channel=channel_id, ts=str(thread_ts), limit=100)['messages']

                # Get the user prompts papertrail
                user_prompts = user_prompt_papertrail(thread_history)

                # Post the user prompts papertrail to Slack
                client.chat_postMessage(
                    channel=channel_id, thread_ts=thread_ts, text=f"User Prompts Papertrail:\n{user_prompts}")
                print("SENDING SLACK AN HTTP200 AFTER POSTING PAPERTRAIL...")
                return make_response("", 200)
            elif thread_ts and event['user'] != bot_user_id:
                print(f"THREADED CHATGPT MESSAGE, INVOKING {bot_user_id} BOT.")
                Thread(target=process_activity, args=(event, VERBOSE_MODE)).start()  
        
            else:
                if (event.get('type') == 'app_mention') or ("@bot" in event_text_blocks):
                    print(f"USER INVOKED BOT, REPLYING TO USER VIA CHATGPT.")
                    Thread(target=process_activity, args=(event, VERBOSE_MODE)).start()  

                elif "$memory" in event_text_blocks:
                    Thread(target=process_activity, args=(event, VERBOSE_MODE)).start()  

                elif "$dalle" in event_text_blocks:
                    print(f"USER INVOKED DALLE, CREATING IMAGE.")
                    dalle_command = event_text_blocks.replace("$dalle", "").strip()
                    n_images, prompt = parse_dalle_command(dalle_command)
                    Thread(target=generate_image, args=(event, channel_id, prompt, n_images, VERBOSE_MODE)).start()

                elif "$chatwithitself" in event_text_blocks:
                    print(f"USER INVOKED CHATWITHITSELF, STARTING CONVERSATION.")
                    convo_rounds = GLOBAL_CONVO_ROUNDS  # default number of rounds

                    # Check if the command contains "--" followed by a number
                    if "--" in event_text_blocks:
                        try:
                            # Extract the number from the string and convert to int
                            convo_rounds = int(event_text_blocks.split("--")[1].strip())
                        except ValueError:
                            # If extraction/conversion fails, convo_rounds stays as the default
                            pass

                    thread_ts = event.get('thread_ts', event.get('ts'))
                    Thread(target=chat_with_itself.chat_with_itself,
                        args=(client, channel_id, bot_user_id, thread_ts, GLOBAL_STARTER_MESSAGE, convo_rounds)).start()

                # Check if bot is directly mentioned or user uses the $jira --query command
                #or
                if (event.get('type') == 'app_mention' or "<@{}>".format(bot_user_id) in event_text_blocks or "$jira --query" in event_text_blocks):

                    if "$jira --query" in event_text_blocks:
                        print(f"USER INVOKED JIRA, FETCHING ISSUES.")
                        issues = get_issues_assigned_to_current_user(payload=event_text_blocks)
                        Thread(target=client.chat_postMessage, kwargs={
                            "channel": channel_id,
                            "blocks": issues['blocks'],
                            "text": "Here are your current issues in JIRA:",
                            "thread_ts": event.get('thread_ts', event.get('ts'))
                        }).start()
                    else:
                        print(f"USER INVOKED BOT, REPLYING TO USER VIA CHATGPT.")
                        Thread(target=process_activity, args=(event, VERBOSE_MODE)).start()  
            
            print("SENDING SLACK AN HTTP200 SO WE CAN CONTINUE PROCESSING...")
            return make_response("", 200)
    else:
        print(f'Unhandled event type: {event_type}')
        return make_response("Unhandled event or message type", 400)

if __name__ == "__main__":
    app.run(port=int(os.getenv('PORT', 3000)))


