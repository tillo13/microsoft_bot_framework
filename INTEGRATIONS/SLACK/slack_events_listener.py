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

#set this to check to not double post
last_bot_message_ts = None

app = Flask(__name__)
slack_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_token)
bot_adapter = Adapter(Bot())

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.get_json()

    if "challenge" in data:
        return make_response(data["challenge"], 200, {"content_type":"application/json"})
    
    if "event" in data:
        event = data["event"]

        # Skip bot's own messages
        if 'subtype' in event and event['subtype'] == 'bot_message':
            return make_response("Ignore bot's own message", 200)

        if ("<@U02GD132UPJ>" in event["text"].lower() or "@bot" in event["text"].lower()):
            channel_id = event['channel']
            thread_ts = event['ts']

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
    return make_response("", 200)

def send_message(channel, thread_ts, bot_message, response_json, entire_json_payload):
    global last_bot_message_ts

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
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{response_json}```",                
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
    response = client.chat_postMessage(channel=channel, thread_ts=thread_ts,
                                       text="A placeholder message will go here.  If this is sent Slack should respond with something like test123.", blocks=message_block)

    # Keep track of the last message's ts
    last_bot_message_ts = response['ts']

if __name__ == "__main__":
    app.run(port=int(os.getenv('PORT', 3000)))