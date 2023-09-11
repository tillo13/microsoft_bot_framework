import requests
import json
import os
from dotenv import load_dotenv
import time
import datetime
import pytz

start_time = time.time()
print("****- BREADCRUMBS -****: Starting the execution timer.")

seattle_tz = pytz.timezone('America/Los_Angeles')
start_dt = datetime.datetime.fromtimestamp(start_time, tz=seattle_tz).isoformat()
print(f"****- BREADCRUMBS -****: Converted the current timestamp into human-readable format for the Seattle timezone. The current time is {start_dt}.")

load_dotenv()
print("****- BREADCRUMBS -****: Loaded environment variables from the .env file.")

directline_secret = os.getenv("AZURE_DIRECT_LINE_SECRET")
directline_url = os.getenv("AZURE_DIRECT_LINE_URL")
headers = {
    'Authorization': 'Bearer ' + directline_secret,
}

response_times = []
total_chars = 0
total_cost = 0
user_messages = 0
bot_responses = 0
cost_per_token = 0.002 / 1000
avg_tokens_per_char = 5  # approximating 5 chars per token

def recv_response(headers, message_url):
    print("****- BREADCRUMBS -****: Waiting for bot reply...")
    start_time = time.time()
    response = requests.get(message_url, headers=headers)
    response.raise_for_status()
    end_time = time.time()
    response_time = end_time - start_time
    response_times.append(response_time)
    global bot_responses
    bot_responses += 1
    message = response.json()["activities"][-1]["text"] if "activities" in response.json() else None
    message_chars = len(message) if message else 0
    global total_chars
    total_chars += message_chars
    print(f"****- BREADCRUMBS -****: Response time for this message was {response_time} seconds.")
    print(f"****- BREADCRUMBS -****: Number of characters in this message: {message_chars} characters.")
    cost = (message_chars / avg_tokens_per_char) * cost_per_token
    global total_cost
    total_cost += cost
    print(f"****- BREADCRUMBS -****: The estimated cost for this message is ${cost:.5f}.")
    return message

def send_message(headers, message_url, message_text):
    print(f"****- BREADCRUMBS -****: Sending message to bot... Message Content: {message_text}")
    message = {
        'type': 'message',
        'from': {
            'id': 'user1',
            'name': 'User1'
        },
        'locale': 'en-US',
        'text': message_text
    }
    response = requests.post(message_url, headers=headers, json=message)
    response.raise_for_status()
    global user_messages
    user_messages += 1
    global total_chars
    total_chars += len(message_text)
    print(f"****- BREADCRUMBS -****: Number of characters in this message: {len(message_text)} characters.")
    print("****- BREADCRUMBS -****: Message sent successfully!")

try:
    response = requests.post(directline_url, headers=headers)
    response.raise_for_status()

    convo = response.json()

    conversation_id = convo['conversationId']
    token = convo['token']

    message_url = f'{directline_url}/{conversation_id}/activities'

    headers['Authorization'] = 'Bearer ' + token

    initial_message_text = "Hello, bot! Tell me a story about Seattle."
    send_message(headers, message_url, initial_message_text)

    for i in range(10):
        last_response = recv_response(headers, message_url)
        print(f"BOT: {last_response}")
        next_message_text = f"What is a thoughtful question to ask about this response to invoke more conversation: {last_response}?"
        print(f"USER: {next_message_text}")
        time.sleep(2)
        send_message(headers, message_url, next_message_text)

    end_time = time.time()
    total_conversation_time = end_time - start_time

    print("\n\nTotal conversation time: {} seconds.".format(total_conversation_time))
    print("Number of user messages: {}".format(user_messages))
    print("Number of bot responses: {}".format(bot_responses))
    print("Total character count: {}".format(total_chars))
    print("Average response time: {} seconds".format(sum(response_times)/len(response_times) if len(response_times) > 0 else 0))
    print("Shortest response time: {} seconds".format(min(response_times) if len(response_times) > 0 else 0))
    print("Longest response time: {} seconds".format(max(response_times) if len(response_times) > 0 else 0))
    print(f"Total estimated cost: ${total_cost:.5f}")
except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as err:
    print("An error occurred: ", err)