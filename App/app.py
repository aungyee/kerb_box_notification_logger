from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from helper import parseNotificationMessage, parseCustomerSupportGateMessage
from helper import writeToNotificationGoogleSheet, writeToSupportGoogleSheet
from config.slack_credentials import SLACK_BOT_TOKEN, APP_LEVEL_TOKEN

app = App(token=SLACK_BOT_TOKEN)


@app.event('message')
def log_message(message):
    if message['channel'] == 'C015S8KQL85' and message['bot_id'] == 'B015TRV9KNF':
        parsed = parseNotificationMessage(message['text'])
        writeToNotificationGoogleSheet(message['ts'], parsed)
    if message['channel'] == 'C01L1SXKYE4' and message['bot_id'] == 'B01K5PW8RTQ':
        parsed = parseCustomerSupportGateMessage(message['text'])
        writeToSupportGoogleSheet(message['ts'], parsed)


if __name__ == '__main__':
    SocketModeHandler(app, APP_LEVEL_TOKEN).start()
