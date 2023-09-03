from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, make_response
from dotenv import load_dotenv
import os
import json

# load environment variables from .env file
load_dotenv('../../.env')

app = Flask(__name__)
slack_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_token)

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.get_json()
    if "challenge" in data:
        return make_response(data["challenge"], 200, {"content_type":"application/json"})

    if "event" in data:
        event = data["event"]

        if 'bot_id' in event:
            return make_response("Success", 200)

        if 'text' in event and ("<@U02GD132UPJ>" in event["text"] or "@bot" in event["text"]):
            channel_id = event['channel']
            thread_ts = event['ts']
            try:
                response = client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=thread_ts,
                    text="You messaged me!")
            except SlackApiError as e:
                assert e.response["error"]
                print(f"Got an error: {e.response['error']}")
    return make_response("", 200)

if __name__ == "__main__":
    app.run(port=int(os.getenv('PORT', 3000)))