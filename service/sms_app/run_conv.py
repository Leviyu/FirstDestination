import base64
import json
import websocket
from twilio.rest import Client

from data.auth.auth_config import TEXT_CONV_ID, TEXT_CONV_TOKEN, TEXT_CONV_SESSION_ID

SID = TEXT_CONV_ID
auth_token = TEXT_CONV_TOKEN
client = Client(SID, auth_token)
conversation_id = TEXT_CONV_SESSION_ID

def web_socket():
    # Create the WebSocket URL
    websocket_url = f'wss://conversations.twilio.com/v1/Conversations/{conversation_id}/Messages'

    # Define a function to handle incoming WebSocket messages
    def on_message(ws, message):
        print("getting new messages")
        message_data = json.loads(message)
        if message_data.get('EventType') == 'onMessageAdd':
            print(f"New message received: {message_data['Message']['Body']}")

    # Create a WebSocket connection
    ws = websocket.WebSocketApp(websocket_url,
                                header=['Authorization: Basic ' + base64.b64encode(
                                    f'{SID}:{auth_token}'.encode()).decode()],
                                on_message=on_message)

    # Start the WebSocket connection
    ws.run_forever()

def web_hooks():
    webhook = client.conversations.v1.configuration.webhooks().fetch()

    print(webhook.method)

def fetch_latest_message():
  messages = client.conversations \
                   .v1 \
                   .conversations(conversation_id) \
                   .messages \
                   .list(order='asc', limit=20)

  for record in messages:
    print(record.body)
def run_conv():
  conv = "what up bro"
  message = client.conversations.v1.conversations('CHa07976dbd7764a249699f5d32cb170c9').messages.create(author='system', body=conv)

def test_single_conversation():
    import websocket
    def on_message(wsapp, message):
        print(message)

    wsapp = websocket.WebSocketApp("wss://testnet-explorer.binance.org/ws/block",
                                   cookie="chocolate", on_message=on_message)
    wsapp.run_forever(origin="testing_websockets.com", host="127.0.0.1")


# Run the WebSocket client
if __name__ == "__main__":
    fetch_latest_message()
