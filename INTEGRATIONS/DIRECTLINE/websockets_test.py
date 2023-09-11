import websocket
import json
import os
from dotenv import load_dotenv
import requests
import threading
import time

# Load environment variables from .env file
load_dotenv()

directline_secret = os.getenv("AZURE_DIRECT_LINE_SECRET")
directline_url = os.getenv("AZURE_DIRECT_LINE_URL")

# Define headers
headers = {
    'Authorization': 'Bearer ' + directline_secret,
}

# Start a conversation
response = requests.post(directline_url, headers=headers)
response.raise_for_status()
convo = response.json()

if 'conversationId' in convo and 'streamUrl' in convo:
    conversation_id = convo['conversationId']
    stream_url = convo['streamUrl']
else:
    print("Invalid JSON response: ", convo)
    exit(1)

# Define on_message event handler
def on_message(ws, message):
    print(f'Received message: {message}')
    # Close the WebSocket connection after receiving the first message
    print("Closing connection...")
    ws.close()

# Define on_error event handler
def on_error(ws, error):
    print(f'Error occurred: {error}')

# Define on_close event handler
def on_close(ws, close_status_code, close_msg):
    print("### Conversation closed ###")

# Define on_open event handler
def on_open(ws):
    print("### Conversation opened ###")

    def send_message(*args):
        message = {
            'type': 'message',
            'from': {
                'id': 'not a computer man',
                'role': 'user'
            },
            'text': 'Hello, bot! tell me a story about Seattle.',
            'locale': 'en-US'
        }
        print("Sending message to Azure...")
        ws.send(json.dumps(message))
        print("Message sent.")
        
        # Close the connection after a delay
        time.sleep(3)
        print("Closing connection...")
        ws.close()

    threading.Thread(target=send_message).start()

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(stream_url,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever()



print("\n*******************\nWHAT JUST HAPPENED: \n"
"\nWebsockets are an advanced communication technology that provides full-duplex communication channels over a single, long-lived connection. It is an ideal choice for scenarios where low-latency, near real-time communication is required, such as chats, multiplayer games, live trading in finance, or collaborative applications.\n"

"An important advantage of WebSockets lies in the fact that it is stateful. Once a socket connection is established, it remains open until the client or server decides to close it, allowing for real-time data flow.\n"
    
"In contrast to the HTTP/ REST communication, where a new connection has to be established for each request (creating some overhead), WebSockets keep the connection open, and can listens for events or send events in real-time, with a lesser overhead.\n"
"###What we just did###:\n1. We started by importing required libraries and loading the necessary environment variables containing the bot secret and url."
"\n"
"2. Then, we built the Authorization headers needed to make a request to the bot."
"\n"
"3. A POST request was sent to start a conversation with the bot. The response from this should include a 'conversationId' and a 'streamUrl', essential for initiating the conversation and establishing the websocket, respectively."
"\n"
"4. We then defined a series of event handlers for the websocket, which would manage communication with the bot once a connection was established. These included:"
"\n\t- 'on_message', which printed received messages to the console"
"\n\t- 'on_error', which handled and printed any error that occurred during the communication"
"\n\t- 'on_close', which logged when the connection was closed"
"\n\t- 'on_open', which logged when communication was begun and also sent a message to the bot"
"\n"
"5. We created and ran a WebSocketApp utilizing the 'streamUrl' from the initial response and the event handlers we defined. This began our communication with the bot."
"\n"
"6. The 'on_open' trigger sent a message to the bot asking it to tell a story about Seattle."
"\n"
"7. The bot's response was received in the 'on_message' trigger and printed to the console."
"\n"
"8. After the first message was received from the bot, we chose to close the session. You could easily modify this to allow ongoing conversation."
"\n"
"Done! We've successfully used a websocket to have a simple conversation with a bot!")