# Setting Up and Running Your Bot Locally with Bot Framework

This guide will take you through the process of setting up and running your bot locally when Azure deployment is not immediately available.

## Prerequisites

- Node.js (Version 10, 12, 14, 16, or 18. Not 19 or 20.)
- [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator/releases)
- Clone of your bot repository or local copy of your bot's code
- [Visual Studio Code](https://code.visualstudio.com/download) (Highly recommended code editor for editing your bot's code)

## Steps

1. **Check Node.js Version**: Open Terminal (for macOS users) or Command Prompt (for Windows users) and run `node -v`. If you don't have Node.js installed, you will need to install it.
   - Installing Node.js on Windows: Download the LTS version of Node.js from [here](https://nodejs.org/en/download/)
   - Installing Node.js on MacOS: It's recommended to use Homebrew. Install Homebrew by following instructions [here](https://brew.sh/) and then install Node.js by running `brew install node@14`.

2. **Check Bot Framework Emulator**: You need to have Microsoft's Bot Framework Emulator installed. If you don't have it already installed, download it from [here](https://github.com/Microsoft/BotFramework-Emulator/releases) and follow the instructions to install.

3. **Navigate to your Bot Directory**: Find the local directory of your bot's code. Then, in Terminal or Command Prompt, navigate to your directory using the `cd` command. For example, if you have your directory on Desktop, use `cd Desktop/botDirectory`.

4. **Install Dependencies**: Once in your bot's directory, run `npm install`. This command installs all the dependencies that your bot needs. 

5. **Enter OpenAI Key**: To connect your bot with OpenAI, you have to enter your OpenAI key into the "openaipoc.dialog" file in your bot's directory. Open the file in VS Code, find where it says "api-key": "HIDDEN_FOR_SECRET" and replace "HIDDEN_FOR_SECRET" with your actual OpenAI key. Save the file after you've made your changes.

6. **Start the Bot**: In the Terminal or Command Prompt, make sure you're still in your bot's directory, then run `node index.js` or `npm start`, depending on the starting command in your `package.json` file. If the bot runs successfully, you should see a message like `server listening on port 3978`.

7. **Test the Bot in Emulator**: Now open the Bot Framework Emulator. Click "Open Bot" and enter your bot's endpoint, which is usually `http://localhost:3978/api/messages`.  Now you can interact with your bot and see the responses in the Emulator.

NOTE: If your bot does not respond as expected, make sure to check the bot's code and `openaipoc.dialog` file to understand its designed functionalities and how it interacts with the Azure OpenAI endpoint. 

And that's it! You've set up and are running your bot locally.