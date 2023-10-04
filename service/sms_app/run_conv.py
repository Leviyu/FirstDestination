import base64
import json
import os

import websocket
from twilio.rest import Client
import asyncio
import websockets

SID = 'ACdc1260be77e49c7942b4c208fb2b8e73'
auth_token = 'a3f8ad2ddd14092137692a849cb96bf1'
client = Client(SID, auth_token)

conversation_id = 'CHa07976dbd7764a249699f5d32cb170c9'


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


def test_me():
    import websocket
    def on_message(wsapp, message):
        print(message)

    wsapp = websocket.WebSocketApp("wss://testnet-explorer.binance.org/ws/block",
                                   cookie="chocolate", on_message=on_message)
    wsapp.run_forever(origin="testing_websockets.com", host="127.0.0.1")


# Run the WebSocket client
if __name__ == "__main__":
    fetch_latest_message()
