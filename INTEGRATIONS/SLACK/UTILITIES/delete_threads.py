import os
import time
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# setting logging
logging.basicConfig(level=logging.DEBUG) 

# loading environment variables
load_dotenv()
slack_token = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=slack_token)
user_token = os.getenv("SLACK_USER_OAUTH_TOKEN")
client_user = WebClient(token=user_token)
channel_id = os.getenv("SLACK_CHANNEL_ID") # channel id

# testing the Slack client
response = client.auth_test()
bot_user_id = response['user_id']  # Add these lines
print('Bot User ID is:', bot_user_id) # 
print('We will only be deleting from:', channel_id) # 

# keyword to filter messages
keyword = "chatwithitself"
keyword = keyword.lower()

# variable to keep track of deleted messages
deleted_count = 0

# fetching message history from the channel
message_history = client.conversations_history(channel=channel_id)

# function for deleting messages
def delete_message(client: WebClient, channel_id: str, ts: str) -> None:
    for _ in range(5):  # Specify your retry limit here.
        try:
            response = client.chat_delete(channel=channel_id, ts=ts)
            if response['ok']:  # If deletion is successful.
                print(f"Deleted message {ts}.")
                return  # Return from the function.

            if response['error'] == 'ratelimited':  # If deletion is rate limited.
                print('Rate limited. Pausing for 60 seconds.')
                time.sleep(60)  # Pause for 60 seconds.
                continue  # Continue retrying after sleeping.

            print(f"Failed to delete message {ts}: {response['error']}")
            return  # If other errors occurred, return from the function.

        except SlackApiError as e:
            if 'error' in e.response:
                print(f"SlackApiError: {e.response['error']} for message {ts}, maybe it was already deleted.")
            else:
                print(f"Unexpected SlackApiError structure: {e.response} for message {ts}")
        except Exception as e:
            print(f"An unexpected error occurred for message {ts}: {str(e)}")

for message in message_history['messages']:
    # deleting messages with keyword
    if keyword in message['text'].lower():
        delete_message(client, channel_id, message['ts'])
        deleted_count += 1

    # identifying orphaned messages
    if 'reply_count' in message and 'reply_users_count' in message:
        if message['reply_count'] > message['reply_users_count']:
            try:
                replies = client.conversations_replies(channel=channel_id, ts=message['thread_ts'])

            except SlackApiError as e:
                logging.error(f'SlackApiError when fetching replies for message {message["thread_ts"]}: {e.response}', exc_info=True)
                print(f"See the file debug.log for detail about the exception when fetching replies.")
                continue
                
            except Exception as e:
                logging.error(f"Unexpected error when fetching replies for message {message['thread_ts']}", exc_info=True)
                print(f"An unexpected error occurred when fetching replies. See the file debug.log for details.")
                continue

            for reply in replies['messages']:
                delete_message(client_user, channel_id, reply['ts'])
                deleted_count += 1

            time.sleep(1)

print(f"Total number of deleted messages: {deleted_count}")