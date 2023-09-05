import json
import logging

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
             "content": "You are a kind, attentive assistant who always looks at specific details from this exact thread conversation and provide accurate responses by referencing exact names, dates, times, and key information from those conversations if available first, prior to hallucinating any answers."
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