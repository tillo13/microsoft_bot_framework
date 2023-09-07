# 3_GIVE_BOT_MEMORY.md

Some of the major updates to the bot: 
-   Highlighting the addition of memory capabilities
-   Adaptive dialogue design outside of OpenAI ($paths to open special invokes)
-   Deeper integration with OpenAI.

## Memory Management in Bot

Essentially, memory management in our bot builds upon the concept of defining properties and managing these properties throughout different stages of the conversation. 

Although we're using chatGPT as our illustration, this kind of memory management is also useful when we need to track user behaviour, user preferences, or the progression of user's input across multiple sessions in various applications. 

Let's look at the properties we’ve added in more detail:

### user.inputData

This property is an array used as the main store for our chat data. The entire conversation between the user and the bot is stored here. Both the user's inputs and bot's responses are saved in this array to keep a record of the conversation flow.

```json
"user.inputData": [
   {
      "role": "user",
      "content": "${turn.activity.text}"
   }
]
```

### user.isNew

This boolean property is used to distinguish new users. At the beginning of the conversation, if the user's ID does not match the bot's ID, this property is set to true.

```json
"$kind":"Microsoft.SetProperty",
"$designer":{
   "id":"3mL2Zc"
},
"property":"user.isNew",
"value":true
```

### temporary properties: turn.newInput & turn.outputData

Both `turn.newInput` and `turn.outputData` are temporary properties used to handle the new user input and bot output during a turn of conversation, before they are appended to `user.inputData`.

```json
"$kind":"Microsoft.SetProperty",
"$designer":{
  "id":"K1OgeX"
},
"property":"turn.newInput",
"value":[
   {
      "role":"user",
      "content":"${turn.activity.text}"
   }
]
```

## Adding Additional Bot Functionality

With memory management properties in place, the bot can now execute additional commands beyond simple command-response structure. We use a `SwitchCondition` action to implement this setup.

```json
"$kind": "Microsoft.SwitchCondition",
"$designer": {
  "id": "switch123",
  "name": "Switch for commands"
},
"condition": "=trim(substring(turn.Activity.Text, 1))",
```
For example, you may add a command that influences the bot's behaviour based on the stored conversation. You can also add a command that performs an operation on the `user.inputData`.

Keep in mind that this approach forms the base for any command added to your bot, extending the bot's capabilities in various domains, for instance:

- **E-commerce bot**: You might allow commands to add items to a shopping cart, where memories are crucial to remember user's shopping list.
- **Financial bot**: Commands could include adding transactions or calculating total expenditure so far within a specified period.
- **Appointment bot**: Commands might allow setting up and reminding users of future appointments, where memories are used to recall set meetings.

In this way, using memory properties and commands, the bot has effectively evolved into having a 'remembering capability' and added functionality.

## Integration with OpenAI

The bot now communicates with the OpenAI API through an HTTP request and we customize the "body" now with the new data.

```json
"$kind":"Microsoft.HttpRequest",
"$designer":{
  "id":"KXxrGs",
  "comment":"Send user input to Azure OpenAI endpoint"
},
"resultProperty":"turn.results",
"method":"POST",
"url":"=settings.OPENAI_API_BASE_URL + '/' + settings.OPENAI_API_DEPLOYMENT + '?api-version=' + settings.OPENAI_API_VERSION",
"body":{ "messages":"=user.inputData" },
"headers":{ "api-key":"=settings.OPENAI_API_KEY" },
"responseType":"json",
"contentType":"application/json"
```

The `body` contains the `user.inputData`, the memory of the conversation, to provide context to the AI model. This will enhance it thorough understanding of preceding interactions, not limited to OpenAI chatbot conversations but also to other AI services, but giving it that sentience.

In conclusion, the new features in your bot, especially with memory-capabilities and making HTTP requests, largely expand its functionality, making it a more effective and efficient conversational assistant.