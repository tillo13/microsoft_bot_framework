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

upload_time = None
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

    upload_url = f'{directline_url}/{conversation_id}/upload?userId=not_a_computer_man'

    headers['Authorization'] = 'Bearer ' + token

    # Create timestamp-named file and write test data into it
    file_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_test.txt"
    with open(file_name, 'w') as file:
        file.write("This is some test data")

    # Open your file in binary mode
    with open(file_name,'rb') as file:
        # Upload your file
        print(f"Uploading and sending an attachment to Azure bot...\n Filename: {file_name}")
        upload_time = time.time()
        response = requests.post(upload_url, headers=headers, data=file)
        response.raise_for_status()

    print("Response Payload: ")
    print(json.dumps(response.json(), indent=4))

except requests.exceptions.RequestException as err:
    print ("Oops: Something Else",err)
print("\nFYI this file will be deleted by Azure within 24 hours.")


end_time = time.time()
end_dt = datetime.datetime.fromtimestamp(end_time, tz=seattle_tz).isoformat()
total_time_elapsed = end_time - start_time

if upload_time:
    print(f"\nTransaction finished!")
    print(f"Script started at: {start_dt}")
    print(f"File uploaded at: {datetime.datetime.fromtimestamp(upload_time, tz=seattle_tz).isoformat()}")
print(f"The script ended at: {end_dt}")
print(f"Total script time to run: {total_time_elapsed:.9f} seconds.")
print("\n*******************\nWHAT JUST HAPPENED: \n"
      "1. The script started and we loaded Direct Line API credentials from the environment. \n"
      "2. A new conversation with the Azure Bot was started. \n"
      "3. Created a new .txt file named with the current datetime and wrote some test data into it. \n"
      "4. That file was uploaded and sent as an attachment to the Azure bot. \n"
      "5. The bot's response to the upload was printed. \n"
      "6. Throughout the process, timestamps were captured at each key stage and total times taken for key interactions were calculated.")