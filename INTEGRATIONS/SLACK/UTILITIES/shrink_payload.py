import re

def remove_extra_spaces_comments(text):
    lines = text.split('\n')
    stripped = [line for line in lines if not line.strip().startswith('#')]
    clean_text = ' '.join(stripped)
    clean_text = re.sub('\s+', ' ', clean_text).strip()  
    clean_text = re.sub('\"\"\"(.*?)\"\"\"', '', clean_text, flags=re.MULTILINE|re.DOTALL) # remove multi-line comments
    clean_text = re.sub("'''(.*?)'''", '', clean_text, flags=re.MULTILINE|re.DOTALL) # remove multi-line comments
    return clean_text
code = """



THREADED CHATGPT MESSAGE, INVOKING U02GD132UPJ BOT.
CURRENT THREAD_TS in def talk_to_chatbot: 2023-09-05 05:16:07.439079
Converted thread_ts in Unix timestamp format: 1693890967.439079
Calling Slack conversations_replies API with channel_id: C05R51F0KL1, thread_ts: 2023-09-05 05:16:07.439079
RESPONSE FROM CONVERSATION ENDPOINT: {'ok': True, 'messages': [{'client_msg_id': '4d0743d9-4642-403a-a6e8-467e5ee5d9d2', 'type': 'message', 'text': 'yo <@U02GD132UPJ> did you know I have a pet cat named ollie?', 'user': 'U0154RCJXJA', 'ts': '1693890967.439079', 'blocks': [{'type': 'rich_text', 'block_id': 'rWEw', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'yo '}, {'type': 'user', 'user_id': 'U02GD132UPJ'}, {'type': 'text', 'text': ' did you know I have a pet cat named ollie?'}]}]}], 'team': 'T015BHH8U5Q', 'thread_ts': '1693890967.439079', 'reply_count': 15, 'reply_users_count': 2, 'latest_reply': '1693891308.666619', 'reply_users': ['U02GD132UPJ', 'U0154RCJXJA'], 'is_locked': False, 'subscribed': False}, {'bot_id': 'B02FPC375QB', 'type': 'message', 'text': 'A placeholder message titled test123.', 'user': 'U02GD132UPJ', 'ts': '1693890969.705469', 'app_id': 'A02FPBY7UTC', 'blocks': [{'type': 'section', 'block_id': 'J2R', 'text': {'type': 'mrkdwn', 'text': "That's cool! Your pet cat named Ollie sounds adorable. Cats can make wonderful companions.", 'verbatim': False}}], 'team': 'T015BHH8U5Q', 'bot_profile': {'id': 'B02FPC375QB', 'app_id': 'A02FPBY7UTC', 'name': 'overthereBot', 'icons': {'image_36': 'https://a.slack-edge.com/80588/img/plugins/app/bot_36.png', 'image_48': 'https://a.slack-edge.com/80588/img/plugins/app/bot_48.png', 'image_72': 'https://a.slack-edge.com/80588/img/plugins/app/service_72.png'}, 'deleted': False, 'updated': 1632691147, 'team_id': 'T015BHH8U5Q'}, 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'client_msg_id': 'd4d75746-ed43-4c8b-a74e-230224c9b503', 'type': 'message', 'text': 'Yea, also I have been to italy.', 'user': 'U0154RCJXJA', 'ts': '1693891089.531209', 'blocks': [{'type': 'rich_text', 'block_id': 'y2Y', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'Yea, also I have been to italy.'}]}]}], 'team': 'T015BHH8U5Q', 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'bot_id': 'B02FPC375QB', 'type': 'message', 'text': 'A placeholder message titled test123.', 'user': 'U02GD132UPJ', 'ts': '1693891091.426419', 'app_id': 'A02FPBY7UTC', 'blocks': [{'type': 'section', 'block_id': '0xW', 'text': {'type': 'mrkdwn', 'text': "That's amazing! When did you visit Italy?", 'verbatim': False}}], 'team': 'T015BHH8U5Q', 'bot_profile': {'id': 'B02FPC375QB', 'app_id': 'A02FPBY7UTC', 'name': 'overthereBot', 'icons': {'image_36': 'https://a.slack-edge.com/80588/img/plugins/app/bot_36.png', 'image_48': 'https://a.slack-edge.com/80588/img/plugins/app/bot_48.png', 'image_72': 'https://a.slack-edge.com/80588/img/plugins/app/service_72.png'}, 'deleted': False, 'updated': 1632691147, 'team_id': 'T015BHH8U5Q'}, 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'client_msg_id': '7e98c9a9-3c5c-4a30-a9e3-027a97b7e7d3', 'type': 'message', 'text': 'nevermind that for now, I have a blue car and am 44.', 'user': 'U0154RCJXJA', 'ts': '1693891115.772229', 'blocks': [{'type': 'rich_text', 'block_id': 'kK=p', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'nevermind that for now, I have a blue car and am 44.'}]}]}], 'team': 'T015BHH8U5Q', 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'bot_id': 'B02FPC375QB', 'type': 'message', 'text': 'A placeholder message titled test123.', 'user': 'U02GD132UPJ', 'ts': '1693891118.764749', 'app_id': 'A02FPBY7UTC', 'blocks': [{'type': 'section', 'block_id': '/Md7f', 'text': {'type': 'mrkdwn', 'text': "Got it! So you have a blue car and you're 44 years old. Is there anything specific you'd like assistance with regarding your car or your age?", 'verbatim': False}}], 'team': 'T015BHH8U5Q', 'bot_profile': {'id': 'B02FPC375QB', 'app_id': 'A02FPBY7UTC', 'name': 'overthereBot', 'icons': {'image_36': 'https://a.slack-edge.com/80588/img/plugins/app/bot_36.png', 'image_48': 'https://a.slack-edge.com/80588/img/plugins/app/bot_48.png', 'image_72': 'https://a.slack-edge.com/80588/img/plugins/app/service_72.png'}, 'deleted': False, 'updated': 1632691147, 'team_id': 'T015BHH8U5Q'}, 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'client_msg_id': '0f30a38a-31cc-4058-8121-2fc2d13a30b1', 'type': 'message', 'text': 'again, not now either, but my pet is 3.', 'user': 'U0154RCJXJA', 'ts': '1693891153.633209', 'blocks': [{'type': 'rich_text', 'block_id': 'sh/qE', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'again, not now either, but my pet is 3.'}]}]}], 'team': 'T015BHH8U5Q', 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'bot_id': 'B02FPC375QB', 'type': 'message', 'text': 'A placeholder message titled test123.', 'user': 'U02GD132UPJ', 'ts': '1693891157.061859', 'app_id': 'A02FPBY7UTC', 'blocks': [{'type': 'section', 'block_id': 'JGXHE', 'text': {'type': 'mrkdwn', 'text': "Ah, I see! So your pet, Ollie, is 3 years old. That's a great age for a pet. Do you have any specific questions or concerns about your lovely pet Ollie?", 'verbatim': False}}], 'team': 'T015BHH8U5Q', 'bot_profile': {'id': 'B02FPC375QB', 'app_id': 'A02FPBY7UTC', 'name': 'overthereBot', 'icons': {'image_36': 'https://a.slack-edge.com/80588/img/plugins/app/bot_36.png', 'image_48': 'https://a.slack-edge.com/80588/img/plugins/app/bot_48.png', 'image_72': 'https://a.slack-edge.com/80588/img/plugins/app/service_72.png'}, 'deleted': False, 'updated': 1632691147, 'team_id': 'T015BHH8U5Q'}, 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'client_msg_id': 'e2b2cef5-3c5f-4d52-b9a4-678ad0a40dea', 'type': 'message', 'text': 'siciliy was pretty cool.', 'user': 'U0154RCJXJA', 'ts': '1693891172.640109', 'blocks': [{'type': 'rich_text', 'block_id': 'aC/', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'siciliy was pretty cool.'}]}]}], 'team': 'T015BHH8U5Q', 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'bot_id': 'B02FPC375QB', 'type': 'message', 'text': 'A placeholder message titled test123.', 'user': 'U02GD132UPJ', 'ts': '1693891175.185999', 'app_id': 'A02FPBY7UTC', 'blocks': [{'type': 'section', 'block_id': 'hpt', 'text': {'type': 'mrkdwn', 'text': "That's great to hear! When did you visit Sicily?", 'verbatim': False}}], 'team': 'T015BHH8U5Q', 'bot_profile': {'id': 'B02FPC375QB', 'app_id': 'A02FPBY7UTC', 'name': 'overthereBot', 'icons': {'image_36': 'https://a.slack-edge.com/80588/img/plugins/app/bot_36.png', 'image_48': 'https://a.slack-edge.com/80588/img/plugins/app/bot_48.png', 'image_72': 'https://a.slack-edge.com/80588/img/plugins/app/service_72.png'}, 'deleted': False, 'updated': 1632691147, 'team_id': 'T015BHH8U5Q'}, 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'client_msg_id': '421de818-0014-4f97-a2f2-a18d2f93e7d9', 'type': 'message', 'text': 'several times.', 'user': 'U0154RCJXJA', 'ts': '1693891201.332469', 'blocks': [{'type': 'rich_text', 'block_id': 'qZR', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'several times.'}]}]}], 'team': 'T015BHH8U5Q', 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'bot_id': 'B02FPC375QB', 'type': 'message', 'text': 'A placeholder message titled test123.', 'user': 'U02GD132UPJ', 'ts': '1693891204.682109', 'app_id': 'A02FPBY7UTC', 'blocks': [{'type': 'section', 'block_id': 'G/a', 'text': {'type': 'mrkdwn', 'text': "I see, you've visited Sicily several times. It must be a place you really enjoy going back to. What was your favorite part about your visits to Sicily?", 'verbatim': False}}], 'team': 'T015BHH8U5Q', 'bot_profile': {'id': 'B02FPC375QB', 'app_id': 'A02FPBY7UTC', 'name': 'overthereBot', 'icons': {'image_36': 'https://a.slack-edge.com/80588/img/plugins/app/bot_36.png', 'image_48': 'https://a.slack-edge.com/80588/img/plugins/app/bot_48.png', 'image_72': 'https://a.slack-edge.com/80588/img/plugins/app/service_72.png'}, 'deleted': False, 'updated': 1632691147, 'team_id': 'T015BHH8U5Q'}, 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'client_msg_id': 'cf7c5341-198b-478d-94aa-60767854ac28', 'type': 'message', 'text': 'who won the war of 1812?', 'user': 'U0154RCJXJA', 'ts': '1693891254.063729', 'blocks': [{'type': 'rich_text', 'block_id': 'aZ8', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'who won the war of 1812?'}]}]}], 'team': 'T015BHH8U5Q', 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'bot_id': 'B02FPC375QB', 'type': 'message', 'text': 'A placeholder message titled test123.', 'user': 'U02GD132UPJ', 'ts': '1693891258.621979', 'app_id': 'A02FPBY7UTC', 'blocks': [{'type': 'section', 'block_id': '4LvPI', 'text': {'type': 'mrkdwn', 'text': 'The War of 1812 was fought between the United States and the United Kingdom. It is often considered to be a draw by many historians, as neither side achieved all of their objectives. However, it resulted in improved relations between the two countries in the years that followed.', 'verbatim': False}}], 'team': 'T015BHH8U5Q', 'bot_profile': {'id': 'B02FPC375QB', 'app_id': 'A02FPBY7UTC', 'name': 'overthereBot', 'icons': {'image_36': 'https://a.slack-edge.com/80588/img/plugins/app/bot_36.png', 'image_48': 'https://a.slack-edge.com/80588/img/plugins/app/bot_48.png', 'image_72': 'https://a.slack-edge.com/80588/img/plugins/app/service_72.png'}, 'deleted': False, 'updated': 1632691147, 'team_id': 'T015BHH8U5Q'}, 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'bot_id': 'B02FPC375QB', 'type': 'message', 'text': 'A placeholder message titled test123.', 'user': 'U02GD132UPJ', 'ts': '1693891260.959489', 'app_id': 'A02FPBY7UTC', 'blocks': [{'type': 'section', 'block_id': '0RL', 'text': {'type': 'mrkdwn', 'text': 'The War of 1812 was fought between the United States and the United Kingdom. It ultimately ended in a stalemate, with no clear winner. Both sides agreed to the Treaty of Ghent in 1814, which restored pre-war boundaries and settled several outstanding issues.', 'verbatim': False}}], 'team': 'T015BHH8U5Q', 'bot_profile': {'id': 'B02FPC375QB', 'deleted': False, 'name': 'overthereBot', 'updated': 1632691147, 'app_id': 'A02FPBY7UTC', 'icons': {'image_36': 'https://a.slack-edge.com/80588/img/plugins/app/bot_36.png', 'image_48': 'https://a.slack-edge.com/80588/img/plugins/app/bot_48.png', 'image_72': 'https://a.slack-edge.com/80588/img/plugins/app/service_72.png'}, 'team_id': 'T015BHH8U5Q'}, 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}, {'client_msg_id': 'd3ef2aba-c09f-4670-b35f-297a5209d8a8', 'type': 'message', 'text': 'my cat is cold, who is my cat and how old is she?', 'user': 'U0154RCJXJA', 'ts': '1693891308.666619', 'blocks': [{'type': 'rich_text', 'block_id': 'dbT', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'my cat is cold, who is my cat and how old is she?'}]}]}], 'team': 'T015BHH8U5Q', 'thread_ts': '1693890967.439079', 'parent_user_id': 'U0154RCJXJA'}], 'has_more': False}
OPENAI PAYLOAD BEFORE SENDING:{
  "messages": [
    {
      "role": "system",
      "content": "You are a kind, attentive assistant who always looks at specific details from this exact thread conversation and provide accurate responses by referencing exact names, dates, times, and key information from those conversations if available first, prior to hallucinating any answers."
    },
    {
      "role": "user",
      "content": "yo <@U02GD132UPJ> did you know I have a pet cat named ollie?"
    },
    {
      "role": "assistant",
      "content": "That's cool! Your pet cat named Ollie sounds adorable. Cats can make wonderful companions."
    },
    {
      "role": "user",
      "content": "Yea, also I have been to italy."
    },
    {
      "role": "assistant",
      "content": "That's amazing! When did you visit Italy?"
    },
    {
      "role": "user",
      "content": "nevermind that for now, I have a blue car and am 44."
    },
    {
      "role": "assistant",
      "content": "Got it! So you have a blue car and you're 44 years old. Is there anything specific you'd like assistance with regarding your car or your age?"
    },
    {
      "role": "user",
      "content": "again, not now either, but my pet is 3."
    },
    {
      "role": "assistant",
      "content": "Ah, I see! So your pet, Ollie, is 3 years old. That's a great age for a pet. Do you have any specific questions or concerns about your lovely pet Ollie?"
    },
    {
      "role": "user",
      "content": "siciliy was pretty cool."
    },
    {
      "role": "assistant",
      "content": "That's great to hear! When did you visit Sicily?"
    },
    {
      "role": "user",
      "content": "several times."
    },
    {
      "role": "assistant",
      "content": "I see, you've visited Sicily several times. It must be a place you really enjoy going back to. What was your favorite part about your visits to Sicily?"
    },
    {
      "role": "user",
      "content": "who won the war of 1812?"
    },
    {
      "role": "assistant",
      "content": "The War of 1812 was fought between the United States and the United Kingdom. It is often considered to be a draw by many historians, as neither side achieved all of their objectives. However, it resulted in improved relations between the two countries in the years that followed."
    },
    {
      "role": "assistant",
      "content": "The War of 1812 was fought between the United States and the United Kingdom. It ultimately ended in a stalemate, with no clear winner. Both sides agreed to the Treaty of Ghent in 1814, which restored pre-war boundaries and settled several outstanding issues."
    },
    {
      "role": "user",
      "content": "my cat is cold, who is my cat and how old is she?"
    }
  ]
}
{'id': 'chatcmpl-7vInVFIc347Cr25XXzcmsj3YbjQ3N', 'object': 'chat.completion', 'created': 1693891309, 'model': 'gpt-35-turbo', 'choices': [{'index': 0, 'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': "Apologies for the confusion earlier. To clarify, according to our previous conversation, your pet cat is named Ollie and is 3 years old. As an AI, I don't have access to personal information unless shared with me in conversation. If you have any concerns about your cat feeling cold, I recommend ensuring they have a warm and comfortable spot to rest, providing them with appropriate bedding or blankets, and keeping the environment cozy for them. If you notice any unusual behavior or symptoms, it may be best to consult with a veterinarian for advice."}}], 'usage': {'completion_tokens': 111, 'prompt_tokens': 482, 'total_tokens': 593}}
{'id': 'chatcmpl-7vInYZrA1IdEIqWyYMQYQsMYOwH65', 'object': 'chat.completion', 'created': 1693891312, 'model': 'gpt-35-turbo', 'choices': [{'index': 0, 'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': "Apologies, but as an AI language model, I don't have access to personal information about individuals unless it has been shared with me in the course of our conversation. I can provide general information and help with various topics. Is there anything else I can assist you with?"}}], 'usage': {'completion_tokens': 55, 'prompt_tokens': 482, 'total_tokens': 537}}
127.0.0.1 - - [04/Sep/2023 22:21:54] "POST /slack/events HTTP/1.1" 200 -
INFO:werkzeug:127.0.0.1 - - [04/Sep/2023 22:21:54] "POST /slack/events HTTP/1.1" 200 -

        
        
        """
clean_code = remove_extra_spaces_comments(code)
print(clean_code)