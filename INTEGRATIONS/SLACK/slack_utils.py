from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import json

slack_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_token)

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

        estimated_cost = total_tokens  * 0.00015
        message_block += [
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text":  f":moneybag: Estimated total running cost: $ {estimated_cost:.5f} (calculated as {total_tokens} tokens x $ 0.00015 per token)"
                    }
                ],
            }
        ]

    client.chat_postMessage(channel=channel, thread_ts=thread_ts,
                            text="A placeholder message titled test123.", blocks=message_block)

    mark_message_processed(channel, thread_ts)
    
def mark_message_processed(channel, timestamp):
    hourglass = 'hourglass'
    check_mark = 'white_check_mark'

    # Remove hourglass reaction
    try:
        client.reactions_remove(
            name=hourglass,
            channel=channel,
            timestamp=timestamp
        )
    except SlackApiError as e:
        print(f"Failed to remove {hourglass} emoji: {e.response['error']}")

    # Add check mark reaction
    try:
        client.reactions_add(
            name=check_mark,
            channel=channel,
            timestamp=timestamp
        )
    except SlackApiError as e:
        print(f"Failed to add {check_mark} emoji: {e.response['error']}")

bot_user_id = client.auth_test()["user_id"]
bot_initiated_threads = []

def get_thread_starter_user_id(channel, thread_ts):
    response = client.conversations_replies(channel=channel, ts=thread_ts)
    starter_message = response['messages'][0]

    starter_user_id = starter_message['user']

    if starter_user_id == bot_user_id and thread_ts not in bot_initiated_threads:
        bot_initiated_threads.append(thread_ts)
        
    return starter_user_id