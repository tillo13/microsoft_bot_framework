#passed in from  from slack_events_listener.py
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

def parse_dalle_command(command_text):
    n_images = 3  # set the default value
    prompt = command_text.strip()
  
    if '--' in command_text:
        command_parts = command_text.split(' ')
        for index, part in enumerate(command_parts):
            if '--' in part:
                try:
                    n_images = min(int(part.replace('--', '')), 5)  # capping images at 5
                    command_parts.pop(index)  # remove this part from the command
                    prompt = ' '.join(command_parts).strip()  # recreate the prompt
                except ValueError:
                    pass
    return n_images, prompt

def generate_image(event, channel_id, prompt, n_images, VERBOSE_MODE):
    print(f"COMMAND RECEIVED: Ask DALL-E for {n_images} images...")
    start_time = time.time() # records the start time

    # Check if entered number was more than limit and send Slack message
    command_parts = event["text"].split(' ')
    for index, part in enumerate(command_parts):
        if '--' in part:
            try:
                entered_number = int(part.replace('--', ''))  
                if entered_number > 5:
                    warning_message = f":exclamation: Doh! You requested {entered_number} images, but the maximum is 5. We'll proceed with 5 images."
                    print(warning_message)  # Output warning message to terminal
                    client.chat_postMessage(channel=channel_id, text=warning_message, thread_ts=event["ts"])  # Send warning to user via Slack
            except ValueError:
                pass

    # Initial message with bot animation and prompt
    initial_message_block = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":robot_face: *Connecting to DALL-E for your {n_images} images, please stand by...*\n\n*...Dall-E is creating for:* `{prompt}`..."
            }
        }
    ]
    
    client.chat_postMessage(
        channel=channel_id,
        thread_ts=event["ts"],
        text="Generating images with DALL-E...",
        blocks=initial_message_block
    )
    # Before entering the for loop
    total_orig_size = 0
    total_final_size = 0

    try: 
        # Request image from DALL-E
        response = openai.Image.create(
            prompt=prompt,
            n=n_images
        )

        # Print the complete response from DALL-E
        print("RESPONSE FROM DALLE_OPENAI: ", response)

        if VERBOSE_MODE:   # if VERBOSE_MODE was passed here as argument
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=event["ts"],
                text = "*VERBOSE MODE ENABLED. Posting DETAILED additional information from the call...*",
            )
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=event["ts"],
                text = f"The DALLE-OPENAI Response: {response}",  # perhaps could choose to prettify
            )

        # Check if folder exists, if not, create it
        if not os.path.exists('GENERATED_IMAGES'):
            os.makedirs('GENERATED_IMAGES')

        #process each file
        for index, image_data in enumerate(response["data"]):
            # Initialize these variables at the start of the loop for each image data
            original_size_in_MB = 0 
            final_size_in_MB = 0 

            image_url = image_data["url"]
            print(f"DALL-E QUERY {index+1} COMPLETED...")
            filename = image_url.split("/")[-1].split("?")[0]  # Filename extracted from URL
            print(f"FILENAME: {filename} \nDALL-E QUERY {index+1} COMPLETED...")

            print("DOWNLOADING GENERATED IMAGE...")
            # Download image
            image_response = requests.get(image_url)
            file_data = image_response.content

            # Original size
            original_size_in_MB = len(file_data) / (1024*1024) # This line was moved up
            total_orig_size += original_size_in_MB  # This line was moved down

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

            print("DOWNLOADING GENERATED IMAGE...")
            # Download image
            image_response = requests.get(image_url)
            file_data = image_response.content

            # Original size
            #original_size_in_MB = len(file_data) / (1024*1024)
            #total_orig_size += original_size_in_MB  # Add original size to the total

            # if image if over 3MB, let's reduce the size
            if len(file_data) > 3e6:  # 3e6 = 3MB
                print("IMAGE SIZE OVER 3MB, STARTING TO RESIZE...")

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
                    img_resized.save(os.path.join('GENERATED_IMAGES', f"dalle_{prompt}_{index+1}_of_{n_images}.png")) 
                    filepath = os.path.join('GENERATED_IMAGES', f"dalle_{prompt}_{index+1}_of_{n_images}.png") 

                if os.path.isfile(filepath):
                    final_size_in_MB = len(file_data) / (1024*1024)  # converted from Bytes to Megabytes
                    size_reduction = original_size_in_MB - final_size_in_MB
                    total_final_size += final_size_in_MB  # Add final size to the total
                    size_reduction_percent = (size_reduction / original_size_in_MB) * 100  # the percentage of the reduction
                    
                    print(f"Original size: {format(original_size_in_MB, '.2f')} MB")
                    print(f"Final size: {format(final_size_in_MB, '.2f')} MB")
                    print(f"Size reduction: {format(size_reduction, '.2f')} MB - {format(size_reduction_percent, '.2f')}%")
                    print("UPLOADING THE RESIZED IMAGE TO SLACK...")

                    try:
                        with open(filepath, 'rb') as file:
                            files = {'file': file}
                            too_large_message = f"{filename} is over 3MB, it's being reduced in size..."
                            payload = {
                                #"initial_comment": filename,
                                "channels": channel_id,
                                "thread_ts": event["ts"],
                            }
                            headers = {
                                "Authorization": "Bearer {}".format(slack_token)
                            }
                            
                            # Here, you are uploading the image first.
                            response = requests.post(
                                "https://slack.com/api/files.upload",
                                headers=headers, files=files, data=payload
                            )
                            if not response.json()['ok']:
                                raise SlackApiError(response.json()['error'])
                            
                            image_num = index + 1  # We add 1 because `index` starts from 0
                            # Now send the image details block message after successful upload
                            block_message = [
                                {
                                    "type": "context",
                                    "elements": [
                                        {
                                            "type": "mrkdwn",
                                            "text": (f":information_source: You asked Dall-E for: `{prompt}` \n"
                                                    f"*This is image:* _{image_num}_ *of* _{n_images}_.\n"        
                                                    f":robot_face: Your prompt was: `$dalle {prompt}`\n" 
                                                    f"*Filename:* `{filename}`\n"
                                                    f"*Azure accessible until:* `{expires_at}`\n"
                                                    f"*Expires in:* `{int(hours)} hours and {int(minutes)} minutes`\n"
                                                    f"*Original file size:* `{format(original_size_in_MB, '.2f')} MB`\n"
                                                    f"*Final file size:* `{format(final_size_in_MB, '.2f')} MB`\n" 
                                                    f"*Size reduction:* `{format(size_reduction, '.2f')} MB` - `{format(size_reduction_percent, '.2f')}%`\n"
                                                    )
                                        }
                                    ]
                                },
                                {
                                    "type": "divider"
                                }
                            ]

                            client.chat_postMessage(
                                channel=channel_id,
                                thread_ts=event["ts"],
                                text=f"Posting image number {image_num+1} generated by DALL-E...",
                                blocks=block_message,
                            )

                            print("IMAGE AND IMAGE DETAILS SUCCESSFULLY UPLOADED TO SLACK...")              

                    except SlackApiError as e:
                        print("FAILED TO UPLOAD THE IMAGE TO SLACK... SENDING THE URL INSTEAD...")
                        client.chat_postMessage(
                            channel=channel_id,
                            thread_ts=event["ts"],
                            text=f"Failed to upload image to Slack: {str(e)}. Here is the URL to your image: {image_url}",
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

    # Summary block
    total_reduction = total_orig_size - total_final_size

    if total_orig_size != 0: 
        total_reduction_percent = (total_reduction / total_orig_size) * 100  # the percentage of the total reduction
    else:
        total_reduction_percent = 0

    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)

    # Prepare summary message
    summary_message = [
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        f"*Summary:* \n"
                        f"You asked for {n_images} images.\n" 
                        f":information_source: Your prompt was: `$dalle {prompt}` \n"
                        f"The total size of all the images was {format(total_orig_size, '.2f')}MB from DALL-E.\n"
                        f"We shrunk them down to {format(total_final_size, '.2f')}MB, a reduction of {format(total_reduction_percent, '.2f')}%.\n"
                        f"The total time to complete this was {int(minutes)} minutes and {int(seconds)} seconds.\n"
                        f"Try again with a new `$dalle` prompt.\n"
                        f"❓Get help at any time with `$help`."
                    )
                }
            ]
        },
        {"type": "divider"},
    ]

    # Post the summary message
    client.chat_postMessage(
        channel=channel_id,
        thread_ts=event["ts"],
        text="Summary of DALL-E image generation request...",
        blocks=summary_message,
    )