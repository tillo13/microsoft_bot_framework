import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

directline_url = "https://directline.botframework.com/v3/directline"

# You need to replace this with the token you got from the previous step
token = "YOUR_TOKEN_FROM_PREVIOUS_STEP"

# Define headers
headers = {
    'Authorization': 'Bearer ' + token,
}

try:
    print("Refreshing the token....")
    response = requests.post(f"{directline_url}/tokens/refresh", headers=headers)
    response.raise_for_status()  # raise exception if invalid response
    refreshed_token_info = response.json()

    print("Refreshed Token Information: ")
    print(refreshed_token_info)

except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)
except requests.exceptions.ConnectionError as errc:
    print("Error Connecting:", errc)
except requests.exceptions.Timeout as errt:
    print("Timeout Error:", errt)
except requests.exceptions.RequestException as err:
    print("Oops: Something Else", err)

print("\n*******************\nWHAT JUST HAPPENED: \n"
    "1. The script started and loaded the Azure Direct Line API endpoint from the environment. \n"
    "2. It then defined a token which had been previously obtained through another process. \n"
    "3. A header was created for the API request, including the bearer token for authentication. \n"
    "4. The script then attempted to refresh the token using a POST request to the /tokens/refresh endpoint. \n"
    "5. If the request was successful, the refreshed token information was printed out. \n"
    "6. If any errors occurred during the request, these were handled and printed out. \n"
    "7. Therefore, the script is designed to refresh an Azure Bot authentication token.")