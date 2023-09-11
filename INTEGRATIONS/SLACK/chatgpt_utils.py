from datetime import datetime
from bot_logic import Bot
from bot_adapter import Adapter
from botbuilder.schema import Activity
from dotenv import load_dotenv
import os
import json
from slack_utils import send_message



from slack_sdk import WebClient

slack_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_token)
bot_adapter = Adapter(Bot(client))

# loading environment variables from .env file
load_dotenv('../../.env')

def process_activity(event, verbose_mode):  
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

    # Deserialize the activity and process it
    message_activity = Activity().deserialize(activity)
    bot_adapter.process_activity(message_activity)

    # Extract the bot message content if present
    if message_activity.bot_responses and 'message_content' in message_activity.bot_responses:
        message_content = message_activity.bot_responses['message_content']
    else:
        message_content = ""

    # Check if 'usage' key exists in message_activity.bot_responses
    if 'usage' in message_activity.bot_responses:
        total_tokens = message_activity.bot_responses['usage'].get('total_tokens', 0)  # retrieving total_tokens from 'usage'
        print(f"Total tokens in process_activity: {total_tokens}")
    else:
        total_tokens = 0

    # Print the bot responses
    print(f"message_activity.bot_responses in chatgpt_utils.py: {message_activity.bot_responses}")

    send_message(
        event["channel"], 
        event["ts"], 
        message_content,
        message_activity.bot_responses.get('details', ''), 
        message_activity.bot_responses.get('entire_json_payload', ''), 
        total_tokens,
        verbose_mode
    )
    
    return message_content