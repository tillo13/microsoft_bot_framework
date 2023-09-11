import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

directline_secret = os.getenv("AZURE_DIRECT_LINE_SECRET")

# Define headers
headers = {
    'Authorization': 'Bearer ' + directline_secret,
}

try:
    print("Generating a new token....")
    response = requests.post("https://directline.botframework.com/v3/directline/tokens/generate", headers=headers)
    response.raise_for_status() # raise exception if invalid response
    token_info = response.json()

    print("Generated Token Information: ")
    print(token_info)

except requests.exceptions.HTTPError as errh:
    print ("Http Error:",errh)
except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc)
except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
except requests.exceptions.RequestException as err:
    print ("Oops: Something Else",err)


print("\n*******************\nWHAT JUST HAPPENED: \n"
    "1. The script started by loading Azure Direct Line API credentials from the environment. \n"
      "2. A new Direct Line API token was requested from Azure by sending a POST request to the Direct Line token generation endpoint. \n"
      "3. If the token was successfully generated, the details of the newly created token were printed out. \n"
      "4. Any exceptions that occurred during the token generation process were caught and the corresponding error messages were printed out. \n"
      "5. At the end of the process, the script either successfully generated and printed a new Direct Line token or printed an error message if something went wrong.")
