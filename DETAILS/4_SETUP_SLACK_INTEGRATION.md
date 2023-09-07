# Creating Integration Paths

In this guide, we'll go through the process of setting up the integration paths so that our bot can communicate with other interfaces like Slack. This is the first of many integrations—once our bot is able to talk to Slack, we can use the same procedure to connect it to other applications. Doing this locally with nGrok and local listeners for test with the idea that we'll host it on Azure soon --this is a good practice for testing anyway...

## Prerequisites

- Your bot is already set up and running locally as shown in earlier guides.
- [Python](https://www.python.org/downloads/) installed (recommended version 3.8+).
- [Slack](https://slack.com/intl/en-us/) account and workspace for testing.
- [Flask](https://flask.palletsprojects.com/en/2.0.x/installation/) installed (Python web framework).
- [Ngrok](https://ngrok.com/download) installed. Ngrok is used to expose local servers (like our Flask app) to the internet.
- The Slack App is created in your slack workspace.

## Steps

1. **Slack App Configuration:** On the Slack API platform, create a new Slack App for your workspace. You should name it based on the bot's duty, '@Bot' for example. You can do this at https://api.slack.com/apps. You'll also be required to set up bot user OAuth Token and app-level token for your bot (they can be found under the *OAuth and Permissions* menu), the bot needs these tokens to authenticate when making API calls. Save these tokens as you'll use them in the later stages. 

2. **Activate Event Subscriptions:** In your Slack App settings, turn the 'Enable Events' on. This enables your bot to listen for events in the Slack workspace. The bot listens to message.posts and emojis creation.

3. **Creating Python Flask Listener:** In order to verify the Slack Event Subscription, a separate Python Flask listener is set up. This independent web server listens on port `3000` by default and uses the route `/slack/events` to accept POST requests. When Slack sends a verification challenge during the Event Subscription process, the listener echoes back the challenge for Slack to complete the verification.

4. **Running Python Flask Listener with Ngrok:** Start the local Flask server by running your Python script (assumed to be called `slack_events_listener.py`)- [slack_events_listener.py example here](https://github.com/tillo13/microsoft_bot_framework/blob/main/INTEGRATIONS/SLACK/slack_events_listener.py) installed (recommended version 3.8+).. In another terminal window, start Ngrok with `ngrok http 3000`. Take note of the provided Ngrok URL— you'll use it to set up the request URL in the Slack App's event subscriptions section. This allows the Slack workspace to send HTTP POST requests to your local server, whenever an event happens.

5. **Ngrok Inspection Interface:** Ngrok provides a local web interface at `http://localhost:4040` to inspect all HTTP traffic through your ngrok tunnel. You see the detailed headers, query parameters, and payload for every request which helps in debugging.

6. **Modifying the Python Flask Webserver:** Modify the `slack_events_listener.py` script to listen for certain keywords in the incoming Slack Event. If a message with those keywords is detected, a function is triggered, making the bot post a message back to the channel where the command was issued. Set the SLACK_BOT_TOKEN from the Slack environment variables as your authentication token for the bot.

7. **Setting Up Environment Variables:** Create a `.env` file and set your `SLACK_BOT_TOKEN` environment variable there (replace **your_bot_token** with the actual bot token).
    ```
    SLACK_BOT_TOKEN="your_bot_token"
    ```

11. **Running the Python Flask App:** After updating the `slack_events_listener.py` script, rerun the Flask app. The Server starts and listens for mentions of the `@bot` text or the Bot User ID in the content of any messages posted in the channel.

## Note

- Each time you restart your Ngrok session, you get a new URL. You must update this new URL in your Slack App configuration so that the events continue to get forwarded to the correct place. Visit `https://api.slack.com/apps -> your_app -> Event Subscriptions -> Enable Events setting` to update the new URL.

- [slack_events_listener.py](https://github.com/tillo13/microsoft_bot_framework/blob/main/INTEGRATIONS/SLACK/slack_events_listener.py) on Github here.
   
This lays the groundwork for integrating the bot with other platforms...