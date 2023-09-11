import os
import threading
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

directline_secret = os.getenv("AZURE_DIRECT_LINE_SECRET")
directline_url = f"https://directline.botframework.com/v3/directline/conversations"

# Define headers
headers = {
    'Authorization': 'Bearer ' + directline_secret,
}

def start_conversation():
    start_time = time.time()
    start_dt = time.ctime(start_time)
    print(f"Conversation started at: {start_dt}")
    try:
        response = requests.post(directline_url, headers=headers)
        response.raise_for_status()  # raise exception if invalid response
        print("Started a conversation: ", response.json())
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Oops: Something Else", err)

    end_time = time.time()
    end_dt = time.ctime(end_time)
    total_time_elapsed = end_time - start_time
    print(f"Conversation finished at: {end_dt}")
    print(f"Total conversation time: {total_time_elapsed:.9f} seconds.")
    
# Start 10 conversations
for i in range(10):
    threading.Thread(target=start_conversation).start()

print("\n*******************\nWHAT JUST HAPPENED: \n"
      "1. The script started and loaded Azure Direct Line API credentials from the environment. \n"
      "2. A function, start_conversation, was defined to start a new conversation with Azure Bot, capturing the start and finish times. \n"
      "3. The script then initiated 10 separate threads, each starting a new conversation with the Azure Bot simultaneously. \n"
      "4. For each conversation, the conversation details were printed out and if any exceptions occurred during the conversation they were handled and printed out. \n"
      "5. At the end of each conversation, the finish time was printed out along with the total time it took for the conversation. \n"
      "6. Hence, in total, 10 separate conversations with the Azure Bot were started and ended concurrently.")