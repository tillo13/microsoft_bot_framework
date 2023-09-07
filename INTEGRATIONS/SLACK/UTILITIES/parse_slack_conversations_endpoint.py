import pprint
import json
import ast

#put the slack payload exactly as is between the triple-quotes

data = '''
{'ok': True, 'messages': [{'client_msg_id': '22aec81c-f4dd-4dc8-943a-290c6b174edf', 'type': 'message', 'text': 'hi <@U02GD132UPJ>', 'user': 'U0154RCJXJA', 'ts': '1693888479.810369', 'blocks': [{'type': 'rich_text', 'block_id': 'WPx2', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'hi '}, {'type': 'user', 'user_id': 'U02GD132UPJ'}]}]}], 'team': 'T015BHH8U5Q', 'thread_ts': '1693888479.810369', 'reply_count': 2, 'reply_users_count': 2, 'latest_reply': '1693888496.057099', 'reply_users': ['U02GD132UPJ', 'U0154RCJXJA'], 'is_locked': False, 'subscribed': False}, {'bot_id': 'B02FPC375QB', 'type': 'message', 'text': 'A placeholder message titled test123.', 'user': 'U02GD132UPJ', 'ts': '1693888482.181809', 'app_id': 'A02FPBY7UTC', 'blocks': [{'type': 'section', 'block_id': 'KC/w', 'text': {'type': 'mrkdwn', 'text': 'Hello! How can I assist you today?', 'verbatim': False}}], 'team': 'T015BHH8U5Q', 'bot_profile': {'id': 'B02FPC375QB', 'deleted': False, 'name': 'overthereBot', 'updated': 1632691147, 'app_id': 'A02FPBY7UTC', 'icons': {'image_36': 'https://a.slack-edge.com/80588/img/plugins/app/bot_36.png', 'image_48': 'https://a.slack-edge.com/80588/img/plugins/app/bot_48.png', 'image_72': 'https://a.slack-edge.com/80588/img/plugins/app/service_72.png'}, 'team_id': 'T015BHH8U5Q'}, 'thread_ts': '1693888479.810369', 'parent_user_id': 'U0154RCJXJA'}, {'client_msg_id': '417ec435-03ae-4c30-99aa-8414fcde8575', 'type': 'message', 'text': 'ok one', 'user': 'U0154RCJXJA', 'ts': '1693888496.057099', 'blocks': [{'type': 'rich_text', 'block_id': 'wBV8a', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'ok one'}]}]}], 'team': 'T015BHH8U5Q', 'thread_ts': '1693888479.810369', 'parent_user_id': 'U0154RCJXJA'}], 'has_more': False}'''

# Fallback GPT-3 message if anything fails in parse
fallback_gpt3_message = [
    {"role": "system", "content": "You are a python script that tried to parse a slack endpoint and could not."},
    {"role": "user", "content": "I will ask again later, but tell me this error happened."}
]

# Flag to check if an error occurred
error_occurred = False

try:
    # Parse the string into python dict
    data_dict = ast.literal_eval(data)

    # Now let's pretty print the dict
    pprint.pprint(data_dict)

    # Counting the number of characters in the json
    json_data = json.dumps(data_dict)
    print("Number of characters: ", len(json_data))

except (ValueError, SyntaxError):
    print("Error: Invalid data format.")
    error_occurred = True
    data_dict = {}

except TypeError:
    print("Error: Unable to process data.")
    error_occurred = True
    data_dict = {}

try:
    # Extract messages
    messages = data_dict.get('messages', [])

    if not messages:
        raise ValueError("No messages in data.")

    # List to hold reformatted messages
    # Initialize with the system message
    gpt3_messages = [
        {
            "role": "system",
            "content": "You are a kind, attentive assistant who always looks at specific details from this exact thread conversation and provide accurate responses by referencing exact names, dates, times, and key information from those conversations if available first, prior to hallucinating any answers."
        }
    ]

    # Loop through messages
    for message in messages:
        try:
            # Initialize content
            content = ''

            # Check if message is from user or bot
            if 'bot_id' in message:
                role = "assistant"
                # Access the 'text' key from 'blocks' list
                content = message.get('blocks', [{}])[0].get('text', {}).get('text', '')
            else:
                role = "user"
                content = message.get('text', '')

            if not content:
                raise ValueError("Content not found in message.")

            # Append reformatted message to list
            gpt3_messages.append({"role": role, "content": content})

        except ValueError as e:
            print(f"Skipping message due to error: {e}")
            error_occurred = True
            continue

    # Use JSON to print in a nice readable format
    print(json.dumps(gpt3_messages, indent=2))

except ValueError as e:
    print(f"Error: {e}")
    error_occurred = True

# If an error occurred at any point, print the fallback GPT-3 messages
if error_occurred:
    print(json.dumps(fallback_gpt3_message, indent=2))