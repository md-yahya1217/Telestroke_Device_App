import websocket
import threading
import json
import logging

class WebSocketClient:
    def __init__(self, url, command_handler):
        self.url = url
        self.command_handler = command_handler
        self.ws = None
        self.thread = None
        self.stop_event = threading.Event()

    def on_message(self,ws, message):
        try:
            command = json.loads(message)
            print(f"Received message: {command}")
            # Forward the command to the command handler
            if self.command_handler:
                self.command_handler(command)
        except Exception as e:
            logging.error(f"Error processing message: {e}")

    def on_error(self, ws, error):
        logging.error(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")

    def on_open(self, ws):
        print("WebSocket opened")

    def run(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.on_open = self.on_open

        def run_websocket():
            self.ws.run_forever()

        self.thread = threading.Thread(target=run_websocket)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join()
