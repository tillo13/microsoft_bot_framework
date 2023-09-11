import requests
import os
from dotenv import load_dotenv
import time
import datetime
import pytz
import json

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

headers['Authorization'] = 'Bearer ' + token

# Get information about the conversation.
conversation_info_get_time = time.time()
response = requests.get(f'{directline_url}/{conversation_id}', headers=headers)
response.raise_for_status() # raise exception if invalid response

# Print out the response
print("Conversation Information: ")
print(json.dumps(response.json(), indent=4))

# end total script timing
end_time = time.time()
end_dt = datetime.datetime.fromtimestamp(end_time, tz=seattle_tz).isoformat()
total_time_elapsed = end_time - start_time

print(f"\nTransaction finished!")
print(f"Script started at: {start_dt}")
print(f"Time to get the conversation information: {time.time() - conversation_info_get_time:.9f} seconds.")
print(f"Script finished at: {end_dt}")
print(f"Total script time to run: {total_time_elapsed:.9f} seconds.")

print("\n*******************\nWHAT JUST HAPPENED: \n"
      "1. The script started and Azure Direct Line API credentials were loaded from the environment. \n"
      "2. A new conversation with the Azure Bot was started using these credentials. \n"
      "3. With the conversation ID obtained from the new conversation, a GET request was made to obtain more information about this conversation. \n"
      "4. The information about the conversation received from Azure Bot was pretty printed on the console. \n"
      "5. Throughout the process, timestamps were captured at each key stage and total times taken for key interactions were calculated.")