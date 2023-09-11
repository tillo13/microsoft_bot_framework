from slack_sdk import WebClient
import os
import time
from dotenv import load_dotenv
from chatgpt_utils import process_activity, send_message

# Add your imports here
import requests


# default number of conversation rounds
##GLOBAL_CONVO_ROUNDS = 2
#GLOBAL_STARTER_MESSAGE ="Please tell me a very short story about Seattle in 5 sentences or less."

def calculate_statistics(thread_messages, bot_id):
      user_messages = 0
      bot_responses = 0
      total_chars = 0
      response_times = []
      last_user_ts = None

      # sorted messages by timestamps
      sorted_messages = sorted(thread_messages, key=lambda x: float(x['ts']))      

      # iterate over sorted messages
      for message in sorted_messages:
          if message['type'] != 'message':
              continue                   # skip non-message event

          ts = float(message['ts'])       # get timestamp

          if message['user'] == bot_id:   # it's a bot message
              bot_responses += 1          # increment bot_responses

              # if we have a user message before this bot message
              if last_user_ts is not None:        
                  response_times.append(ts - last_user_ts)   # calculate response time

          else:                          # it's a user message
              user_messages += 1

          total_chars += len(message['text'])   # calculate total characters

          # after calculating response time, update last_user_ts
          last_user_ts = ts                     

      avg_response_time = sum(response_times) / len(response_times) if response_times else 0
      min_response_time = min(response_times) if response_times else 0
      max_response_time = max(response_times) if response_times else 0

      return user_messages, bot_responses, total_chars, avg_response_time, min_response_time, max_response_time

def chat_with_itself(client, channel_id, bot_id, thread_ts, starter_message, rounds=10):

    def send_message_as_bot(bot_name, message):
        message_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{bot_name}:* {message}"
                }
            }
        ]
        client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=message, blocks=message_blocks)

    response_times = []
    total_chars = 0
    total_cost = 0
    user_messages = 0
    bot_responses = 0
    cost_per_token = 0.002 / 1000
    avg_tokens_per_char = 5  # approximating 5 chars per token

    # Post the starter message in the thread where $chatwithitself was invoked
    send_message_as_bot("ROBOT1", starter_message)
    total_chars += len(starter_message)
    user_messages += 1 

    conversation_counter = 0
    while conversation_counter < rounds:
        # Wait for the bot to respond
        time.sleep(10)

        # Fetch the thread history
        thread_history = client.conversations_replies(channel=channel_id, ts=thread_ts, limit=10)['messages']
        print(thread_history)

        for message in reversed(thread_history):
            # If bot message is found, respond to it and break the loop
            if message.get('type') == 'message' and message.get('user') == bot_id:
                # Fetch the bot_message
                bot_message = message.get('text')

                # Pass the bot_message to Azure Bot, get the response and show it as "ROBOT2"
                headers = { 'api-key': os.getenv('OPENAI_API_KEY') }
                url = f'{os.getenv("OPENAI_API_BASE_URL")}/{os.getenv("OPENAI_API_DEPLOYMENT")}?api-version={os.getenv("OPENAI_API_VERSION")}'
                data = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are trying to be a good conversationalist. First comment on the question, then please generate a thoughtful question based on the below, and limit your response to just one or two sentences."
                            },
                            {
                                "role": "user",
                                "content": bot_message
                            }
                        ]
                    }
                print(f"Reqeust JSON: {data}")
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    message_content = result['choices'][0]['message']['content']

                    print(f"BOT: {message_content}")
                    print(f"Payload returned: {result}")

                    # show the message on Slack as "ROBOT2"
                    send_message_as_bot("ROBOT2", message_content)

                    # Now, instead of having AI generate continuation, generate a question for the response
                    question_message = f"What is a thoughtful question to ask about this story to invoke more of the conversation in one sentence?: {message_content}?"
                    question_data = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are trying to be a good conversationalist. First comment on the question, then please generate a thoughtful question based on the below, and limit your response to just one or two sentences."
                            },
                            {
                                "role": "user",
                                "content": question_message
                            }
                        ]
                    }
                    print(f"Request JSON: {question_data}")
                    question_response = requests.post(url, headers=headers, json=question_data)
                    if question_response.status_code == 200:
                        question_result = question_response.json()
                        question_content = question_result['choices'][0]['message']['content']

                        print(f"BOT: {question_content}")
                        print(f"Payload returned: {question_result}")

                        # show the generated question on Slack as "ROBOT1"
                        send_message_as_bot("ROBOT1", question_content)
                        conversation_counter += 1
                        user_messages += 1
                        total_chars += len(question_content)
                    else:
                        print(f"An error occurred when communicating with the bot: {question_response.json()}")
                
                else:
                    print(f"An error occurred when communicating with the bot: {response.json()}")

                break

    total_cost = (total_chars / avg_tokens_per_char) * cost_per_token
    # Fetch the entire conversation and calculate statistics
    thread_history = client.conversations_replies(channel=channel_id, ts=thread_ts, limit=1000)['messages']
    user_msgs, bot_msgs, total_chars, avg_resp_time, min_resp_time, max_resp_time = calculate_statistics(thread_history, bot_id)

    print("\n\nTotal conversation rounds: {}".format(rounds))
    print("Number of user messages: {}".format(user_msgs))
    print("Number of robot responses: {}".format(bot_msgs))
    print("Total character count: {}".format(total_chars))
    print("Average response time: {} seconds".format(avg_resp_time))
    print("Shortest response time: {} seconds".format(min_resp_time))
    print("Longest response time: {} seconds".format(max_resp_time))

    # Estimate the cost
    total_tokens = total_chars / avg_tokens_per_char
    total_cost = total_tokens * cost_per_token

    summary_message = f"Total conversation rounds: {rounds}\n" \
                f"Number of user messages: {user_msgs}\n" \
                f"Number of bot responses: {bot_msgs}\n" \
                f"Total character count: {total_chars}\n" \
                f"Average response time: {avg_resp_time} seconds\n" \
                f"Shortest response time: {min_resp_time} seconds\n" \
                f"Longest response time: {max_resp_time} seconds\n" \
                f"Total cost: {total_cost}"

    send_message_as_bot("SUMMARY", summary_message)