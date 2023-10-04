import websocket
import _thread
import time
import rel

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
websocket_url = f'wss://conversations.twilio.com/v1/Conversations/{conversation_id}/Messages'


def on_message(ws, message):
    print("getting new messages")
    message_data = json.loads(message)
    if message_data.get('EventType') == 'onMessageAdd':
        print(f"New message received: {message_data['Message']['Body']}")

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")

if __name__ == "__main__":
    websocket.enableTrace(True)
    # ws = websocket.WebSocketApp("wss://api.gemini.com/v1/marketdata/BTCUSD",
    #                           on_open=on_open,
    #                           on_message=on_message,
    #                           on_error=on_error,
    #                           on_close=on_close)
    ws = websocket.WebSocketApp(websocket_url,
                                header=['Authorization: Basic ' + base64.b64encode(
                                    f'{SID}:{auth_token}'.encode()).decode()],
                                on_message=on_message)

    ws.run_forever(dispatcher=rel, reconnect=100)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()