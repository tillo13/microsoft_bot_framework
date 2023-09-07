import openai
from slack_sdk import WebClient
from dotenv import load_dotenv
from urllib.parse import unquote, urlparse
from datetime import datetime
import os

# loading environment variables from .env file
load_dotenv('../../.env')

# setting OpenAI variables
openai.api_key = os.getenv('OPENAI_DALLE_API_KEY')
openai.api_type = "azure"
openai.api_base = os.getenv('OPENAI_DALLE_BASE_URL')
openai.api_version = os.getenv('OPENAI_DALLE_VERSION')

# initializing slack client
slack_token = os.getenv('SLACK_BOT_TOKEN')
client = WebClient(token=slack_token)

def generate_image(event, channel_id, prompt):
    # Indicate DALL-E query has started
    client.chat_postMessage(
        channel=channel_id,
        thread_ts=event["ts"],
        text="Querying DALL-E, please hold...",
    )

    response = openai.Image.create(
        prompt=prompt,
        n=1
    )

    image_url = response["data"][0]["url"]

    # parsing SAS token for image details
    parsed = urlparse(image_url)
    sas_token = dict((k, unquote(v)) for k, v in (item.split('=') for item in parsed.query.split('&')))

    # Parse the SAS token data into a more human-readable message
    expires_at = datetime.strptime(sas_token.get('se'), '%Y-%m-%dT%H:%M:%SZ')
    now = datetime.utcnow()
    time_remain = expires_at - now
    hours, remainder = divmod(time_remain.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    
    
    
    # Parse the SAS token data into a more human-readable message
    expires_at = datetime.strptime(sas_token.get('se'), '%Y-%m-%dT%H:%M:%SZ')
    sas_details = f"Image will be accessible until: {expires_at} (in about {int(hours)} hours and {int(minutes)} minutes)\n"
    sas_details += f"Allowed Protocols: {sas_token.get('spr')}\n"  # https
    sas_details += f"Resource type: {sas_token.get('sr')} (b = blob)\n"  # b means blob type
    sas_details += f"Storage Services Version (sv): {sas_token.get('sv')}\n"
    sas_details += f"Permissions (sp): {sas_token.get('sp')}\n"  # r means read access
    sas_details += f"Signature (sig) for the token: [HIDDEN FOR SECURITY]\n"  # Signature should be hidden for security reasons
    sas_details += f"Storage Service Version ID (skoid): {sas_token.get('skoid')}\n"
    sas_details += f"Signing Key (sks): {sas_token.get('sks')}\n" 
    sas_details += f"Key Start Time (skt): {sas_token.get('skt')}\n" 
    sas_details += f"Tenant ID for Azure Storage Service (sktid): {sas_token.get('sktid')}\n"
    
    block = [
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": prompt,
            },
            "image_url": image_url,
            "alt_text": "DALLE image"
        }
    ]

    client.chat_postMessage(
        channel=channel_id,
        thread_ts=event["ts"],
        text="Image Generated",
        blocks=block
    )

    # Send the SAS details to the same channel
    client.chat_postMessage(
        channel=channel_id,
        thread_ts=event["ts"],
        text=f"DALLE SAS Details:\n{sas_details}",
    )