import requests
import json
import os
from dotenv import load_dotenv
import time
import datetime
import pytz

# start script timing to see how long it takes
start_time = time.time()

# Convert timestamp to human-readable format and Seattle timezone
seattle_tz = pytz.timezone('America/Los_Angeles')
start_dt = datetime.datetime.fromtimestamp(start_time, tz=seattle_tz).isoformat()

print(f"Script started at: {start_dt}")

# Load environment variables from .env file
load_dotenv()

directline_secret = os.getenv("AZURE_DIRECT_LINE_SECRET")
directline_url = os.getenv("AZURE_DIRECT_LINE_URL")
headers = {
    'Authorization': 'Bearer ' + directline_secret,
}

try:
    # Start a conversation
    print("Starting a conversation with Azure...")
    response = requests.post(directline_url, headers=headers)
    response.raise_for_status()
    convo = response.json()

    if 'conversationId' in convo and 'token' in convo:
        conversation_id = convo['conversationId']
        token = convo['token']
    else:
        print("Invalid JSON response: ", convo)
        exit(1)

    message_url = f'{directline_url}/{conversation_id}/activities'

    headers['Authorization'] = 'Bearer ' + token

    # Send a message to Azure bot
    print("Sending message to Azure bot...")
    message = {
        'type': 'message',
        'from': {
            'id': 'not a computer man',
            'role': 'user'
        },
        'text': 'Hello, bot! How are you?',
        'locale': 'en-US'
    }

    print("Request Payload: ")
    print(json.dumps(message, indent=4))

    response = requests.post(message_url, headers=headers, json=message)
    message_send_time = time.time()
    response.raise_for_status()

    # Wait for a response from Azure bot
    print("Getting response from Azure bot...")
    time.sleep(5)
    response = requests.get(message_url, headers=headers)
    response.raise_for_status()

    print("Response Payload: ")
    print(json.dumps(response.json(), indent=4))

    # Get all activities
    print("Getting all activities from the conversation...")
    response = requests.get(f'{directline_url}/{conversation_id}/activities', headers=headers)
    response.raise_for_status()
    activities = response.json()

    print("Activities in Conversation: ")
    print(json.dumps(activities, indent=4))

except requests.exceptions.RequestException as err:
    print ("Oops: Something Else",err)

end_time = time.time()
end_dt = datetime.datetime.fromtimestamp(end_time, tz=seattle_tz).isoformat()
total_time_elapsed = end_time - start_time

print(f"\nTransaction finished!")
print(f"Script started at: {start_dt}")
print(f"Sent to Azure at: {datetime.datetime.fromtimestamp(message_send_time, tz=seattle_tz).isoformat()}")
print(f"Transaction finished at: {end_dt}")
print(f"Total script time to run: {total_time_elapsed:.9f} seconds.")
print("\n*******************\nWHAT JUST HAPPENED: \n"
      "1. The script started, and we loaded Direct Line API credentials from the environment. \n"
      "2. A new conversation with the Azure Bot was started. \n"
      "3. A text message was sent to the Azure bot. \n"
      "4. We waited for a response from Azure bot. \n"
      "5. All activities from the conversation were retrieved and printed. \n"
      "6. Throughout this process, timestamps were captured at each key stage, and total time taken was calculated.")