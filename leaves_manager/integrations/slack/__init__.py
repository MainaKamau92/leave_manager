from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackCentral:

    def __init__(self, token):
        self.client = WebClient(token)

    def join_conversation(self, channel):
        return self.client.conversations_join(channel=channel)

    def post_to_channel(self, channel, message, blocks=None):
        try:
            return self.client.chat_postMessage(channel=channel, text=message, blocks=blocks)
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
