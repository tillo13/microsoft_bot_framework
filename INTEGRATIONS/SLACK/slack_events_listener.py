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

# load environment variables from .env file
load_dotenv('../../.env')

VERBOSE_MODE = False  # Set to True for verbose output to slack showing json

app = Flask(__name__)
slack_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_token)
bot_adapter = Adapter(Bot())

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

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.get_json()
    if "challenge" in data:
        return make_response(data["challenge"], 200, {"content_type":"application/json"})
    if "event" in data:
        event = data["event"]
        if 'subtype' in event and event['subtype'] == 'bot_message':
            return make_response("Ignore bot's own message", 200)
        if event['user'] == bot_user_id:  # Ignore events from the bot itself
            return make_response("", 200)
        thread_ts = event.get('thread_ts')
        if thread_ts and event['user'] != bot_user_id:  # Check user is not the bot
            conversation = client.conversations_replies(channel=event['channel'], ts=thread_ts)
            if any(message['user'] == bot_user_id for message in conversation['messages']):
                print("THREADED CHATGPT MESSAGE, INVOKING BOT.")
                process_activity(event)
        else:
            if ("<@U02GD132UPJ>" in event["text"].lower() or "@bot" in event["text"].lower()):
                print("USER INVOKED BOT, REPLYING TO USER VIA CHATGPT.")
                process_activity(event)
            else:
                print("USER INTERACTED, BUT DID NOT CALL BOT.")
    return make_response("", 200)

def process_activity(event):
    channel_id = event['channel']
    thread_ts = event.get('thread_ts')

    activity = {
        "type": "message",
        "text": event["text"],
        "channelId": "slack",
        "conversation": {"id": channel_id,},
        "from": {"id": event.get("user_id")},
    }
    message_activity = Activity().deserialize(activity)
    bot_adapter.process_activity(message_activity)

    # unpack the dictionary to pass the values as arguments
    output = Thread(target=send_message, args=(event["channel"], event["ts"], 
                                        message_activity.bot_responses['message_content'],
                                        message_activity.bot_responses['details'],
                                        message_activity.bot_responses['entire_json_payload']
                                        ))
    output.start()

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