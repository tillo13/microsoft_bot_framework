from botbuilder.core import BotAdapter, TurnContext

class Adapter(BotAdapter):
    def __init__(self, bot):
        self.bot = bot

    def send_activities(self, context: TurnContext, activities):
        return [0] * len(activities)

    def update_activity(self, context, activity):
        pass

    def delete_activity(self, context, reference):
        pass

    def process_activity(self, activity):
        turn_context = TurnContext(self, activity)
        self.run_pipeline(self.bot.on_turn(turn_context))
