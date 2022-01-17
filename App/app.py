from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from helper import parseMessage
from helper import writeToGoogleSheet
from config.slack_credentials import SLACK_BOT_TOKEN, APP_LEVEL_TOKEN

app = App(token=SLACK_BOT_TOKEN)


@app.event('message')
def log_message(message):
    print(message)
    if message['channel'] == 'C015S8KQL85' and message['bot_id'] == 'B015TRV9KNF':
        parsed = parseMessage(message['text'])
        writeToGoogleSheet(message['ts'], parsed)


if __name__ == '__main__':
    SocketModeHandler(app, APP_LEVEL_TOKEN).start()