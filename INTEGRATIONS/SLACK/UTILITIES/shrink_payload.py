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