import json
import logging

def user_prompt_papertrail(data):
    user_prompts = ''
    for message in data:
        if 'bot_id' not in message:
            ts = message.get('ts')
            content = message.get('text', '')
            user_prompts += f"{ts}: {content}\n"
    return user_prompts

def slack_to_chatgpt_parser(data):

    fallback_gpt3_message = [
        {"role": "system", "content": "You are a python script that tried to parse a slack endpoint and could not."},
        {"role": "user", "content": "I will ask again later, but tell me this error happened."}
    ]

    try:
        if not data: 
            raise ValueError("No data to parse.")

        gpt3_messages = [
            {
             "role": "system", 
             "content": "You are a diligent and courteous assistant. Give utmost priority to details provided earlier in each thread of conversation. Always review the history before formulating a response, keeping in mind that users are generally from Teradata so if the question is about data analytics or similar, subtly use this information. Ensure your responses heavily draw from the established context and information already shared in the conversation. Navigate inaccuracies delicately, by asking clarifying questions instead of directly contradicting the user."
            }
        ]

        for message in data:
            try:
                content = ''
                if 'bot_id' in message:
                    role = "assistant"
                    content = message.get('blocks', [{}])[0].get('text', {}).get('text', '')
                else:
                    role = "user"
                    content = message.get('text', '')

                if not content:
                    raise ValueError("Content not found in message.")

                gpt3_messages.append({"role": role, "content": content})

            except ValueError as e:
                logging.warning(f"Skipping message due to error: {e}")
                continue
            
        logging.info("SUCCESSFULLY PARSED SLACK CONVERSATION PAYLOAD")  # Info message after successful parsing
        return gpt3_messages

    except ValueError as e:
        logging.error(f"Error: {e}")
        logging.error("ERRORED ON PARSING SLACK CONVERSATION PAYLOAD, INVESTIGATE!")  # Error message after failed parsing
        return fallback_gpt3_message