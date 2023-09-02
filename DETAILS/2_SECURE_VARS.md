# Secure Setup Guide 

This guide will help you to setup your bot securely by obscuring sensitive data using environment variables.

## Steps

1. **Install the dotenv package**: The `dotenv` package lets you load environment variables from a `.env` file into `process.env`. Install it by running the command `npm install dotenv`.

2. **Create a .env file**: In the root of your project, create a new file named `.env`.

3. **Add Environment Variables**: Add the following lines to the `.env` file. Replace `your_api_key_here` and `your_api_endpoint_here` with your actual OpenAI key and endpoint respectively.
    ```
    OPENAI_API_KEY="your_api_key_here"
    OPENAI_API_BASE_URL="base_url_here"
    OPENAI_API_DEPLOYMENT="deployment_path_here"
    OPENAI_API_VERSION="api_version_here"
    ```

5. **Load Environment Variables**: Require and configure dotenv at the very top of your `index.js` or the entry point file of your project. Add the following code at the top of your `index.js` file:

    ```javascript
    require('dotenv').config();
    ```

6. **Ignore Sensitive Files**: Update your '.gitignore' file to ignore the `.env` file by adding the line `.env` to '.gitignore'. This step is important to make sure your sensitive data is not accidentally pushed to public repositories.

Your `.gitignore` file should look something like this after the addition:

    ```
    generated/
    node_modules/
    .env
    package-lock.json
    .DS_Store
    ```

7. **Update code to use environment variables**: Replace any sensitive values in your code with references to these environment variables. 
   
   Example: 
   ```json
   {
     "$kind": "Microsoft.HttpRequest",
     "resultProperty": "turn.results",
     "method": "POST",
     "url": "=settings.OPENAI_API_BASE_URL + '/' + settings.OPENAI_API_DEPLOYMENT + '?api-version=' + settings.OPENAI_API_VERSION",
     "body": {
       "messages": [
          {"role": "system", "content": "helpful assistant"},
          {"role": "user", "content": "${turn.activity.text}"}
       ]
     },
     "headers": {"api-key": "=settings.OPENAI_API_KEY"},
     "responseType": "json"
   }
   ```
   
And there you have it! You have successfully obscured sensitive data in your code. Now you can safely host your bot on public platforms like GitHub, while keeping your crucial data secure and uniterrupted.