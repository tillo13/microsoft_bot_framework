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

    #test starter:
    print(f"Starter message: {starter_message}")
    starter_user_id = starter_message['user']

    if starter_user_id == bot_user_id and thread_ts not in bot_initiated_threads:
        bot_initiated_threads.append(thread_ts)
        
    return starter_user_id

# initialize empty lists in the global scope
bot_replied_to_messages_ts = []

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

def send_message(channel, thread_ts, bot_message, response_json, entire_json_payload, total_tokens, verbose_mode):
    formatted_response_str = json.dumps(response_json, indent=2)

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

        # Add cost calculation here
    with open('openai_costs_2023sept7.json') as f:
        costs = json.load(f)

    # openai costs in USD per token
    openai_cost_per_token = costs["Language Models"]["GPT-3.5 Turbo"]["4K context"]["Input"]
    openai_cost_per_token = float(openai_cost_per_token) # ensure it's a float

    # Tokens used calculation
    tokens_used = float(total_tokens) 

    print(f"Total tokens: {total_tokens}")
    print(f"Cost per token: {openai_cost_per_token}")
    estimated_cost = tokens_used  * openai_cost_per_token

    # Calculate the cost 
    estimated_cost = tokens_used  * openai_cost_per_token
    #estimated_cost = tokens_used  * openai_cost_per_token * 100  # Multiplied by 100 here for demonstration purposes
    print("Estimated cost in chatgpt_utils.py: {:.10f}".format(estimated_cost))



    message_block += [
        {
            "type": "divider"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text":  f":moneybag: Estimated total running cost: $ {estimated_cost:.5f} (calculated as {total_tokens} tokens x $ {openai_cost_per_token:.5f} per token)"
                }
            ],
        }
    ]

    client.chat_postMessage(channel=channel, thread_ts=thread_ts,
                            text="A placeholder message titled test123.", blocks=message_block)