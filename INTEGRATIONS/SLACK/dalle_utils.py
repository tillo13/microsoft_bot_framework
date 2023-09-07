import openai
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from urllib.parse import unquote, urlparse
from datetime import datetime
import os
import requests
from PIL import Image
from io import BytesIO
import time
import sys
import traceback


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
    print("Asking DALL-E for 3 images...")
    client.chat_postMessage(
        channel=channel_id,
        thread_ts=event["ts"],
        text="Asking DALL-E for 3 images...",
    )

    try: 
        # Request image from DALL-E
        response = openai.Image.create(
            prompt=prompt,
            n=5
        )

        # Print the complete response from DALL-E
        print("RESPONSE FROM DALLE_OPENAI: ", response)

        # Check if folder exists, if not, create it
        if not os.path.exists('GENERATED_IMAGES'):
            os.makedirs('GENERATED_IMAGES')

        #process each file
        for index, image_data in enumerate(response["data"]):
            image_url = image_data["url"]
            print(f"DALL-E QUERY {index+1} COMPLETED...")
            filename = image_url.split("/")[-1].split("?")[0]  # Filename extracted from URL
            print(f"FILENAME: {filename} \nDALL-E QUERY {index+1} COMPLETED...")

            # parsing SAS token for image details
            parsed = urlparse(image_url)
            sas_token = dict((k, unquote(v)) for k, v in (item.split('=') for item in parsed.query.split('&')))

            # Parse the SAS token data into a more human-readable message
            expires_at = datetime.strptime(sas_token.get('se'), '%Y-%m-%dT%H:%M:%SZ')
            now = datetime.utcnow()
            time_remain = expires_at - now
            hours, remainder = divmod(time_remain.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)

            sas_details = f'Filename: {filename}\n'  
            sas_details += f"Azure accessible until: {expires_at}.\n"
            sas_details += f"Therefore, expires in about {int(hours)} hours and {int(minutes)} minutes)\n"
            #sas_details += f"Allowed Protocols: {sas_token.get('spr')}\n"  # https
            #sas_details += f"Resource type: {sas_token.get('sr')} (b = blob)\n"  # b means blob type
            #sas_details += f"Storage Services Version (sv): {sas_token.get('sv')}\n"
            #sas_details += f"Permissions (sp): {sas_token.get('sp')}\n"  # r means read access
            #sas_details += f"Signature (sig) for the token: [HIDDEN FOR SECURITY]\n"  # Signature should be hidden for security reasons
            #sas_details += f"Storage Service Version ID (skoid): {sas_token.get('skoid')}\n"
            #sas_details += f"Signing Key (sks): {sas_token.get('sks')}\n" 
            #sas_details += f"Key Start Time (skt): {sas_token.get('skt')}\n" 
            #sas_details += f"Tenant ID for Azure Storage Service (sktid): {sas_token.get('sktid')}\n"

            # Send the SAS details to the same channel
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=event["ts"],
                text=f"DALLE creation details...\n{sas_details}",
            )

            print("DOWNLOADING GENERATED IMAGE...")
            # Download image
            image_response = requests.get(image_url)
            file_data = image_response.content

            # if image if over 3MB, let's reduce the size
            if len(file_data) > 3e6:  # 3e6 = 3MB
                print("IMAGE SIZE OVER 3MB, STARTING TO RESIZE...")
                client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=event["ts"],
                    text=f"{filename} is over 3MB, it's being reduced in size...",

                )

                img = Image.open(BytesIO(file_data))
                scale_factor = 1

                
                # original size
                original_size_in_MB = len(file_data) / (1024*1024)

                while len(file_data) > 2e6:
                    scale_factor *= 0.9
                    new_size = (int(img.size[0] * scale_factor), int(img.size[1] * scale_factor))
                    img_resized = img.resize(new_size)
                    print(f"IMAGE RESIZED TO : {new_size}")

                    byte_arr = BytesIO()
                    img_resized.save(byte_arr, format='PNG')
                    file_data = byte_arr.getvalue()
                    img_resized.save(os.path.join('GENERATED_IMAGES', f"dalle_{prompt}_{index}.png"))  # Save image to generated images directory
                    filepath = os.path.join('GENERATED_IMAGES', f"dalle_{prompt}_{index}.png")

                if os.path.isfile(filepath):
                    final_size_in_MB = len(file_data) / (1024*1024)  # converted from Bytes to Megabytes
                    size_reduction = original_size_in_MB - final_size_in_MB
                    size_reduction_percent = (size_reduction / original_size_in_MB) * 100  # the percentage of the reduction
                    
                    print(f"Original size: {format(original_size_in_MB, '.2f')} MB")
                    print(f"Final size: {format(final_size_in_MB, '.2f')} MB")
                    print(f"Size reduction: {format(size_reduction, '.2f')} MB - {format(size_reduction_percent, '.2f')}%")
                    print("UPLOADING THE RESIZED IMAGE TO SLACK...")

                    client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=event["ts"],
                    text=f"Original size: {format(original_size_in_MB, '.2f')} MB. \nFinal size: {format(final_size_in_MB, '.2f')} MB. \nSize was reduced by {format(size_reduction, '.2f')} MB - {format(size_reduction_percent, '.2f')}%",
                    )
                try:
                    with open(filepath, 'rb') as file:
                        files = {'file': file}
                        too_large_message = f"{filename} is over 3MB, it's being reduced in size..."
                        payload = {
                            "initial_comment": filename,
                            "channels": channel_id,
                            "thread_ts": event["ts"],
                        }
                        headers = {
                            "Authorization": "Bearer {}".format(slack_token)
                        }
                        response = requests.post(
                            "https://slack.com/api/files.upload",
                            headers=headers, files=files, data=payload
                        )
                        if not response.json()['ok']:
                            raise SlackApiError(response.json()['error'])
                    print("IMAGE UPLOADED SUCCESSFULLY TO SLACK...")
                except SlackApiError as e:
                    print("FAILED TO UPLOAD THE IMAGE TO SLACK... SENDING THE URL INSTEAD...")
                    client.chat_postMessage(
                        channel=channel_id,
                        thread_ts=event["ts"],
                        text=f"Failed to upload image to Slack: {str(e)}. Here is the URL to your image: {image_url}",
                    )

    except SlackApiError as e:
        print("Slack API Error:", str(e))
        error_message = f"Encountered an error while working with Slack: {str(e)}. Please try again later."
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=event["ts"],
            text= error_message
        )

    except openai.error.OpenAIError as o:
        if "safety system" in str(o):
            print("Inappropriate content detected by OpenAI's safety system.")
            error_message = f"OUT OF AN ABUNDANCE OF CAUTION, OPENAI FLAGGED THE IMAGE `{filename}` AS INAPPROPRIATE, TRY AGAIN."
        else:
            print("OpenAI API Error:", str(o))
            error_message = f"Encountered an error while working with OpenAI: {str(o)}. Please try again later."
            
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=event["ts"],
            text= error_message
        )

    except Exception as e:
        error_type, error_value, error_traceback = sys.exc_info()
        tb_str = traceback.format_exception(error_type, error_value, error_traceback)
        slack_error_message = f"Hm, looks like we hit a snag.  Try again later, or ping andy."
        print_error_message = f"An error occurred while processing the image: {str(e)}. Please try again later."

        print(print_error_message)
        
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=event["ts"],
            text= slack_error_message
        )

    except Exception as e:  # Catch-all for other exceptions.
        error_type, error_value, error_traceback = sys.exc_info()
        tb_str = traceback.format_exception(error_type, error_value, error_traceback)
        error_message = f"Error: {error_value} \n {''.join(tb_str)}"
        print(error_message)
