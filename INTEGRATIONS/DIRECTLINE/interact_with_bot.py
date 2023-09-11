import requests
import json
import os
from dotenv import load_dotenv
import time
import datetime
import pytz

# start timer to see how long it takes
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

message_receive_time = None
try:
    print("Starting a conversation with Azure...")
    # Start a conversation
    response_start_time = time.time()
    response = requests.post(directline_url, headers=headers)
    response.raise_for_status() # raise exception if invalid response
    conversation_time = time.time() - response_start_time
    convo = response.json()

    if 'conversationId' in convo and 'token' in convo:
        conversation_id = convo['conversationId']
        token = convo['token']
    else:
        print("Invalid JSON response: ", convo)
        exit(1)

    # Timer for URL building
    print("Building the URL for the message...")
    url_start_time = time.time()
    message_url = f'{directline_url}/{conversation_id}/activities'
    url_end_time = time.time()
    url_building_time = url_end_time - url_start_time

    headers['Authorization'] = 'Bearer ' + token
    message = {
        'type': 'message',
        'from': {
            'id': 'not a computer man',
            'role': 'user'
        },
        'text': 'Hello, bot! tell me a story about seattle.',
        'locale': 'en-US'
    }
    # Print the request payload
    print("Sending message to Azure...")
    print("Request Payload: ")
    print(json.dumps(message, indent=4))
    # Send the message
    message_send_time = time.time()
    response = requests.post(message_url, headers=headers, json=message)
    response.raise_for_status() # raise exception if invalid response
    # Get the bot's response
    print("Getting response from Azure...")
    response = requests.get(message_url, headers=headers)
    response.raise_for_status() # raise exception if invalid response
    message_receive_time = time.time()
    azure_processing_time = message_receive_time - message_send_time
    # Print out the response
    print("Response Payload: ")
    print(json.dumps(response.json(), indent=4))
except requests.exceptions.HTTPError as errh:
    print ("Http Error:",errh)
except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc)
except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
except requests.exceptions.RequestException as err:
    print ("Oops: Something Else",err)

# end total script timing
end_time = time.time()
end_dt = datetime.datetime.fromtimestamp(end_time, tz=seattle_tz).isoformat()
total_time_elapsed = end_time - start_time

if message_receive_time:
    print(f"\nTransaction finished!")
    print(f"Script started at: {start_dt}")
    print(f"Time to build the URL: {url_building_time:.9f} seconds.")
    print(f"Sent to Azure at: {datetime.datetime.fromtimestamp(message_send_time, tz=seattle_tz).isoformat()}")
    print(f"Received a response from Azure at: {datetime.datetime.fromtimestamp(message_receive_time, tz=seattle_tz).isoformat()}")
    print(f"Total Azure processing time: {azure_processing_time:.9f} seconds")
print(f"Script finished at: {end_dt}")
print(f"Total script time to run: {total_time_elapsed:.9f} seconds.")
print("\n*******************\nWHAT JUST HAPPENED: \n"
      "1. The script started and we loaded Direct Line API credentials from the environment. \n"
      "2. A new conversation with the Azure Bot was started. \n"
      "3. A URL was built for a new message to be sent to the bot. \n"
      "4. A message was sent to the Azure Bot asking to tell a story about Seattle. \n"
      "5. We waited for a response from Azure Bot. \n"
      "6. Once the message was received, we pretty printed the response. \n"
      "7. Throughout the process, timestamps were captured at each key stage and total times taken for key interactions were calculated.")