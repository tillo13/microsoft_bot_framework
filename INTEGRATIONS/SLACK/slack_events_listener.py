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
from dalle_utils import generate_image


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
        # Retrieve channel_id from the event data:
        channel_id = event['channel']

        # Ignore bot's own messages
        if event.get('subtype') == 'bot_message' or event.get('user') == bot_user_id:
            return make_response("Ignore bot message", 200)
        event_text_blocks = message_from_blocks(event).lower()
        thread_ts = event.get('thread_ts')
        if thread_ts and event['user'] != bot_user_id:
            print(f"THREADED CHATGPT MESSAGE, INVOKING {bot_user_id} BOT.")
            Thread(target=process_activity, args=(event,)).start()  # start a new thread to process the activity
        else:
            if (event.get('type') == 'app_mention') or ("@bot" in event_text_blocks):
                print(f"USER INVOKED BOT, REPLYING TO USER VIA CHATGPT.")
                Thread(target=process_activity, args=(event,)).start()  # start a new thread to process the activity

            elif "$dalle" in event_text_blocks:
                print(f"USER INVOKED DALLE, CREATING IMAGE.")
                prompt = event_text_blocks.replace("$dalle", "").strip()  # get prompt from user's message
                Thread(target=generate_image, args=(event, channel_id, prompt)).start()

            else:
                print("USER USED SLACK, BUT DID NOT CALL BOT.")
        print("SENDING SLACK AN HTTP200 SO WE CAN CONTINUE PROCESSING...")
    return make_response("", 200)  # Respond immediately to Slack

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