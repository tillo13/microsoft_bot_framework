from jira import JIRA
import os
from dotenv import load_dotenv

# loading environment variables from .env file
load_dotenv('../../.env')

# Get the API token from the environment variable
api_token = os.getenv('2023sept8_JIRA_TOKEN')
username = os.getenv('2023sept8_JIRA_USERNAME')
jira_server = os.getenv('2023sept8_JIRA_SERVER')

# Specify the server of your JIRA instance
jira = JIRA(server=jira_server, basic_auth=(username, api_token))


def get_issues_assigned_to_current_user(payload=None):
    print(f"The payload received from Slack is: {payload}")
    issues = jira.search_issues('assignee = currentUser()')
    blocks = []

    for issue in issues:
        issue_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":information_source: *<{issue.permalink()}|{issue.key}>*: `{issue.fields.summary}`"
            }
        }
        blocks.append(issue_block)
        blocks.append({"type": "divider"})

    return {"blocks": blocks}