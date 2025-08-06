import socket
import json
import threading
import time
from src.client.protocols import Protocols

class Network:
    def __init__(self, host="127.0.0.1", port=8765):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.player_id = None
        self.username = None
        self.incoming_messages = []
        self.running = True
        self.connected = False

    def connect(self, username):
        try:
            self.client.connect((self.host, self.port))
            self.connected = True
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True 
            receive_thread.start()

            welcome_message = self.wait_for_message("welcome")
            if welcome_message:
                self.player_id = welcome_message['data']['player_id']
                print(f"Connected to server. My Player ID is: {self.player_id}")
                self.set_username(username)
                return self.player_id
            return None
        except socket.error as e:
            print(f"Could not connect to server: {e}")
            self.connected = False
            return None

    def receive_messages(self):
        buffer = ""
        while self.running:
            try:
                data = self.client.recv(2048).decode('utf-8')
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message:
                        try:
                            parsed_message = json.loads(message)
                            self.incoming_messages.append(parsed_message)
                        except json.JSONDecodeError:
                            print(f"Received invalid JSON: {message}")
            except socket.error as e:
                print(f"Error receiving data: {e}")
                self.running = False
                self.connected = False
                break
    
    def wait_for_message(self, msg_type, timeout=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            for msg in self.incoming_messages:
                if msg.get("type") == msg_type:
                    self.incoming_messages.remove(msg)
                    return msg
            time.sleep(0.1)
        return None

    def send(self, data):
        if not self.connected:
            print("Not connected to server.")
            return
        try:
            self.client.sendall((json.dumps(data) + '\n').encode('utf-8'))
        except socket.error as e:
            print(f"Failed to send data: {e}")
            self.connected = False

    def set_username(self, username):
        self.username = username
        self.send({
            "type": "set_username",
            "username": username
        })
        print(f"Username '{username}' sent to server.")

    def join_waiting_room(self, game_mode):
        self.send({
            "type": "join_waiting",
            "game_mode": game_mode
        })
        print(f"Request to join {game_mode} waiting room sent.")
        
    def get_message(self):
        if self.incoming_messages:
            return self.incoming_messages.pop(0)
        return None

    def disconnect(self):
        self.running = False
        self.client.close()
        print("Disconnected from server.")
        
    def send_invite(self, target_player_id):
        self.send({
            "type": Protocols.Request.INVITE_PLAYER,
            "target_id": target_player_id
        })

    def respond_to_invite(self, inviter_id, accepted):
        self.send({
            "type": Protocols.Request.INVITE_RESPONSE,
            "inviter_id": inviter_id,
            "accepted": accepted
        })