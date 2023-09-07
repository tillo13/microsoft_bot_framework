from datetime import datetime
from bot_logic import Bot
from bot_adapter import Adapter
from botbuilder.schema import Activity
from slack_sdk import WebClient
from dotenv import load_dotenv
import os
import json

# loading environment variables from .env file
load_dotenv('../../.env')

slack_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_token)
bot_adapter = Adapter(Bot(client))

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

def process_activity(event, verbose_mode):  # add verbose_mode here
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
        message_activity.bot_responses['entire_json_payload'], 
        verbose_mode
    )

def send_message(channel, thread_ts, bot_message, response_json, entire_json_payload, verbose_mode):
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

    if verbose_mode:
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