import socket
import threading
import json
import uuid
import time
from datetime import datetime
from src.server.protocols import Protocols
from src.server.room import RoomManager

BULLET_SPEED = 700

def check_collision(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    if (x1 < x2 + w2 and x1 + w1 > x2 and
        y1 < y2 + h2 and y1 + h1 > y2):
        return True
    return False

class Server:
    def __init__(self, host="127.0.0.1", port=8765):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        
        self.players = {}  
        self.player_sockets = {}  
        self.player_status = {} # connected, waiting, in_game
        self.player_rooms = {}  
        self.player_usernames = {}  
        self.username_to_player = {} 
        self.room_manager = RoomManager()
        
        print(f"Server started on {self.host}:{self.port}")


    def handle_connect(self, client):
        try:
            player_id = str(uuid.uuid4())
            self.players[client] = player_id
            self.player_sockets[player_id] = client
            self.player_status[player_id] = "connected"
            
            self.send(Protocols.Response.WELCOME, {
                "player_id": player_id,
                "message": "Connected to game server"
            }, client)
            
            print(f"Player {player_id} connected from {client.getpeername()}")
            
            self.handle_client(client, player_id)
            
        except Exception as e:
            print(f"Error handling connection: {e}")
        finally:
            self.disconnect(client)

    def handle_client(self, client, player_id):
        buffer = ""
        while True:
            try:
                data = client.recv(2048).decode("utf-8")
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    if message_str:
                        message = json.loads(message_str)
                        self.handle_message(message, player_id)

            except json.JSONDecodeError:
                self.send(Protocols.Response.ERROR, f"Invalid JSON format: {message_str}", client)
            except Exception as e:
                print(f"Error handling message from {player_id}: {e}")
                break
            
    def handle_message(self, message, player_id):
        msg_type = message.get("type")
        
        if msg_type == Protocols.Request.SET_USERNAME:
            self.set_username(player_id, message)
        elif msg_type == Protocols.Request.SEARCH_PLAYER:
            self.search_player(player_id, message)
        elif msg_type == Protocols.Request.REQUEST_GAME:
            self.request_game(player_id, message)
        elif msg_type == Protocols.Request.JOIN_WAITING:
            self.join_waiting_room(player_id, message.get("game_mode", "1v1"))
        elif msg_type == Protocols.Request.LEAVE_WAITING:
            self.leave_waiting_room(player_id)
        elif msg_type == Protocols.Request.GAME_ACTION:
            self.handle_game_action(player_id, message)
        elif msg_type == Protocols.Request.PLAYER_ELIMINATED:
            self.handle_player_eliminated(player_id)
        elif msg_type == Protocols.Request.INVITE_PLAYER:
            self.handle_invite(player_id, message)
        elif msg_type == Protocols.Request.INVITE_RESPONSE:
            self.handle_invite_response(player_id, message)
        else:
            self.send(Protocols.Response.ERROR, f"Unknown message type: {msg_type}", 
                     self.player_sockets[player_id])

    def set_username(self, player_id, message):
        username = message.get("username")
        if not username:
            self.send(Protocols.Response.ERROR, "Username is required", 
                     self.player_sockets[player_id])
            return
        
        if username in self.username_to_player and self.username_to_player[username] != player_id:
            self.send(Protocols.Response.ERROR, "Username already taken", 
                     self.player_sockets[player_id])
            return
        
        self.player_usernames[player_id] = username
        self.username_to_player[username] = player_id
        
        print(f"Player {player_id} set username to: {username}")
        
        self.send(Protocols.Response.USERNAME_SET, {
            "username": username,
            "player_id": player_id
        }, self.player_sockets[player_id])
    
    def search_player(self, player_id, message):
        search_id = message.get("player_id")
        if not search_id:
            self.send(Protocols.Response.ERROR, "Player ID is required", 
                     self.player_sockets[player_id])
            return
        
        if search_id in self.player_sockets:
            username = self.player_usernames.get(search_id, "Unknown")
            self.send(Protocols.Response.PLAYER_FOUND, {
                "player_id": search_id,
                "username": username,
                "status": self.player_status.get(search_id, "unknown")
            }, self.player_sockets[player_id])
        else:
            self.send(Protocols.Response.PLAYER_NOT_FOUND, {
                "message": "Player not found"
            }, self.player_sockets[player_id])
    
    def request_game(self, player_id, message):
        target_player_id = message.get("player_id")
        game_mode = message.get("game_mode", "1v1")
        
        if target_player_id:
            if target_player_id not in self.player_sockets:
                self.send(Protocols.Response.ERROR, "Player not found", 
                         self.player_sockets[player_id])
                return
            
            target_status = self.player_status.get(target_player_id)
            if target_status != "connected":
                self.send(Protocols.Response.ERROR, "Player is not available for game", 
                         self.player_sockets[player_id])
                return
            
            self.create_direct_game(player_id, target_player_id, game_mode)
        else:
            self.join_waiting_room(player_id, game_mode)
    
    def create_direct_game(self, player1_id, player2_id, game_mode="1v1"):
        if game_mode == "1v1":
            players = [player1_id, player2_id]
        else:
            ready_players = self.room_manager.get_ready_players("2v2", 2)
            if len(ready_players) < 2:
                self.send(Protocols.Response.ERROR, "Not enough players for 2v2 game", 
                          self.player_sockets[player1_id])
                return
            players = [player1_id, player2_id] + ready_players
        
        room_id = self.room_manager.create_room(players, game_mode)
        room = self.room_manager.get_room(room_id)
        
        for player_id in players:
            self.player_status[player_id] = "in_game"
            self.player_rooms[player_id] = room_id
        
        print(f"Created direct {game_mode} game room {room_id}")
        
        player_details = {
            p_id: {"username": self.player_usernames.get(p_id, "Unknown")} for p_id in players
        }

        room_message = {
            "room_id": room_id,
            "players": player_details, 
            "game_mode": game_mode,
            "team1": room.team1,
            "team2": room.team2
        }
        
        for player_id in players:
            self.send(Protocols.Response.ROOM_CREATED, room_message, 
                      self.player_sockets[player_id])
        
        self.start_countdown(room_id)
    
    def join_waiting_room(self, player_id, game_mode="1v1"):
        position = self.room_manager.add_to_waiting_queue(player_id, game_mode)
        self.player_status[player_id] = "waiting"
        
        print(f"Player {player_id} joined {game_mode} waiting room")
        
        self.send(Protocols.Response.WAITING_JOINED, {
            "position": position,
            "game_mode": game_mode
        }, self.player_sockets[player_id])
        
        self.check_for_room_creation(game_mode)

    def leave_waiting_room(self, player_id):
        self.room_manager.remove_from_waiting_queue(player_id)
        
        if player_id in self.player_status:
            self.player_status[player_id] = "connected"
            print(f"Player {player_id} left waiting room")

    def check_for_room_creation(self, game_mode="1v1"):
        max_players = 4 if game_mode == "2v2" else 2
        ready_players = self.room_manager.get_ready_players(game_mode, max_players)
        
        if len(ready_players) >= max_players:
            all_waiting = all(self.player_status.get(pid) == "waiting" for pid in ready_players)
            
            if all_waiting:
                self.create_room(ready_players, game_mode)
            else:
                for player_id in ready_players:
                    if self.player_status.get(player_id) == "waiting":
                        self.room_manager.add_to_waiting_queue(player_id, game_mode)

    def create_room(self, players, game_mode="1v1"):
        room_id = self.room_manager.create_room(players, game_mode)
        room = self.room_manager.get_room(room_id)
        for player_id in players:
            self.player_status[player_id] = "in_game"
            self.player_rooms[player_id] = room_id
        
        print(f"Created {game_mode} room {room_id} with players: {players}")

        player_details = {
            p_id: {"username": self.player_usernames.get(p_id, "Unknown")} for p_id in players
        }
        
        room_message = {
            "room_id": room_id,
            "players": player_details,
            "game_mode": game_mode,
            "team1": room.team1,
            "team2": room.team2
        }
       
        for player_id in players:
            if player_id in self.player_sockets:
                self.send(Protocols.Response.ROOM_CREATED, room_message, self.player_sockets[player_id])
        
        self.start_countdown(room_id)

    def start_countdown(self, room_id):
        self.room_manager.set_room_status(room_id, "countdown")
        room = self.room_manager.get_room(room_id)
        room.countdown_start = datetime.now()
        
        print(f"Starting countdown for room {room_id}")
        
        for i in range(3, 0, -1):
            countdown_data = {"seconds": i}
            for player_id in room.players:
                self.send(Protocols.Response.COUNTDOWN, countdown_data, 
                         self.player_sockets[player_id])
            time.sleep(1)
        
        self.room_manager.set_room_status(room_id, "playing")
        game_start_data = {"message": "Game started!"}
        for player_id in room.players:
            self.send(Protocols.Response.GAME_START, game_start_data, 
                     self.player_sockets[player_id])
        
        print(f"Game started in room {room_id}")
                    
    def handle_game_action(self, player_id, message):
        room_id = self.player_rooms.get(player_id)
        if not room_id: return
        room = self.room_manager.get_room(room_id)
        if not room: return

        action = message.get("action")
        
        if action == "player_update":
            player_data = message.get("data", {})
            
            if player_id in room.player_states:
                room.player_states[player_id]['pos'] = player_data.get('pos')
                room.player_states[player_id]['face_right'] = player_data.get('face_right')

            message_to_forward = {
                "player_id": player_id,
                "action": action,
                "data": player_data
            }
            for other_id in room.players:
                if other_id != player_id and other_id in self.player_sockets:
                    self.send(Protocols.Response.GAME_ACTION, message_to_forward, self.player_sockets[other_id])

        elif action == "attack":
            attack_info = {"attacker_id": player_id}
            for p_id in room.players:
                if p_id in self.player_sockets:
                    self.send(Protocols.Response.GAME_ACTION, {"action": "player_attacked", "data": attack_info}, self.player_sockets[p_id])
            
            attacker_state = room.player_states.get(player_id)
            if not attacker_state or not attacker_state.get('pos'): return

            attacker_pos = attacker_state['pos']
            is_facing_right = attacker_state['face_right']
            
            attack_width = 80
            attack_height = 60
            
            if is_facing_right:
                attack_rect = (attacker_pos[0], attacker_pos[1], attack_width, attack_height)
            else:
                attack_rect = (attacker_pos[0] - attack_width, attacker_pos[1], attack_width, attack_height)
            
            for victim_id in room.players:
                if victim_id == player_id: continue

                victim_state = room.player_states.get(victim_id)
                if not victim_state or not victim_state.get('pos'): continue
                
                victim_pos = victim_state['pos']
                victim_rect = (victim_pos[0], victim_pos[1], 40, 80)

                if check_collision(attack_rect, victim_rect):
                    if room.player_health[victim_id] > 0:
                        room.player_health[victim_id] -= 1
                        
                        print(f"HIT! Attacker: {player_id}, Victim: {victim_id}, New Health: {room.player_health[victim_id]}")

                        damage_info = {
                            "victim_id": victim_id,
                            "attacker_id": player_id,
                            "new_health": room.player_health[victim_id]
                        }
                        for p_id in room.players:
                            if p_id in self.player_sockets:
                                self.send(Protocols.Response.PLAYER_TOOK_DAMAGE, damage_info, self.player_sockets[p_id])
                        
                        if room.player_health[victim_id] <= 0:
                            self.handle_player_eliminated(victim_id)
                    
                    break

        elif action == "shoot":
            shoot_data = message.get("data", {})

            bullet_id = f"bullet_{player_id}_{time.time()}"

            new_bullet = {
                "bullet_id": bullet_id,
                "owner_id": player_id,
                "pos": list(shoot_data.get("pos")),
                "direction": shoot_data.get("direction")
            }
            room.bullets[bullet_id] = new_bullet

            for p_id in room.players:
                if p_id in self.player_sockets:
                    self.send(Protocols.Response.GAME_ACTION, {"action": "new_bullet", "data": new_bullet}, self.player_sockets[p_id])

    def handle_player_eliminated(self, player_id):
        room_id = self.player_rooms.get(player_id)
        if not room_id:
            self.send(Protocols.Response.ERROR, "Not in a game room", 
                     self.player_sockets[player_id])
            return
        
        if self.room_manager.eliminate_player(room_id, player_id):
            elimination_data = {
                "player_id": player_id,
                "username": self.player_usernames.get(player_id, "Unknown")
            }
            
            room = self.room_manager.get_room(room_id)
            for other_player_id in room.players:
                if other_player_id != player_id:
                    self.send(Protocols.Response.PLAYER_ELIMINATED, elimination_data, 
                             self.player_sockets[other_player_id])
            
            self.check_game_end(room_id)
    
    def check_game_end(self, room_id):
        room = self.room_manager.get_room(room_id)
        if not room:
            return
        
        team1_alive = sum(1 for pid in room.team1 if room.player_health.get(pid, 0) > 0)
        team2_alive = sum(1 for pid in room.team2 if room.player_health.get(pid, 0) > 0)
        
        if team1_alive == 0 or team2_alive == 0:
            winning_team = 2 if team1_alive == 0 else 1
            winning_players = room.team2 if team1_alive == 0 else room.team1
            
            game_end_data = {
                "winning_team": winning_team,
                "winning_players": winning_players,
                "reason": "team_eliminated"
            }
            
            for player_id in room.players:
                self.send(Protocols.Response.GAME_ENDED, game_end_data, 
                         self.player_sockets[player_id])
            
            self.room_manager.remove_room(room_id)
            for player_id in room.players:
                if player_id in self.player_rooms:
                    del self.player_rooms[player_id]
                self.player_status[player_id] = "connected"
            
            print(f"Game ended in room {room_id}, team {winning_team} won")

    def disconnect(self, client):
        player_id = self.players.get(client)
        if not player_id:
            return
        
        username = self.player_usernames.get(player_id, "Unknown")
        print(f"Player {player_id} ({username}) disconnected")
        
        self.room_manager.remove_from_waiting_queue(player_id)
        
        room_id = self.player_rooms.get(player_id)
        if room_id:
            self.handle_room_disconnection(player_id, room_id)
        
        if client in self.players:
            del self.players[client]
        if player_id in self.player_sockets:
            del self.player_sockets[player_id]
        if player_id in self.player_status:
            del self.player_status[player_id]
        if player_id in self.player_rooms:
            del self.player_rooms[player_id]
        if player_id in self.player_usernames:
            username = self.player_usernames[player_id]
            if username in self.username_to_player:
                del self.username_to_player[username]
            del self.player_usernames[player_id]
        
        client.close()

    def handle_room_disconnection(self, player_id, room_id):
        room = self.room_manager.get_room(room_id)
        if not room:
            return

        for other_player_id in room.players:
            if other_player_id != player_id and other_player_id in self.player_sockets:
                self.send(Protocols.Response.PLAYER_LEFT, {"player_id": player_id}, 
                          self.player_sockets[other_player_id])
  
        if len(room.players) <= 1:
            if room.status == "playing":
                for other_player_id in room.players:
                    if other_player_id != player_id and other_player_id in self.player_sockets:
                        self.send(Protocols.Response.GAME_ENDED, 
                                  {"reason": "player_disconnected"}, 
                                  self.player_sockets[other_player_id])
            
            self.room_manager.remove_room(room_id)
            print(f"Removed room {room_id}")

    def send(self, r_type, data, client):
        try:
            message = {"type": r_type, "data": data}
            message_str = json.dumps(message) + '\n'
            client.send(message_str.encode("utf-8"))
        except Exception as e:
            print(f"Error sending message: {e}")

    # server/main.py
# ... (داخل کلاس Server)

    def game_loop(self):
        while True:
            for room_id in list(self.room_manager.rooms.keys()):
                room = self.room_manager.get_room(room_id)
                if room and room.status == "playing":
                    self.update_room_bullets(room)

                    bullets_data = list(room.bullets.values())
                    for player_id in room.players:
                        if player_id in self.player_sockets:
                            self.send(Protocols.Response.GAME_ACTION, {"action": "bullets_update", "data": bullets_data}, self.player_sockets[player_id])
            time.sleep(1/60)

    def receive(self):
        print("Waiting for connections...")
        game_loop_thread = threading.Thread(target=self.game_loop)
        game_loop_thread = threading.Thread(target=self.game_loop)
        game_loop_thread.daemon = True
        game_loop_thread.start()

        while True:
            try:
                client, address = self.server.accept()
                print(f"New connection from {address}")
                thread = threading.Thread(target=self.handle_connect, args=(client,))
                thread.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")
                break

    def handle_invite(self, inviter_id, message):
        target_id = message.get("target_id")
        
        if not target_id or target_id not in self.player_sockets:
            self.send(Protocols.Response.INVITE_FAILED, {"reason": "Player not found."}, self.player_sockets[inviter_id])
            return
        
        if self.player_status.get(target_id) != "connected":
            self.send(Protocols.Response.INVITE_FAILED, {"reason": "Player is busy."}, self.player_sockets[inviter_id])
            return
        
        if target_id == inviter_id:
            self.send(Protocols.Response.INVITE_FAILED, {"reason": "You cannot invite yourself."}, self.player_sockets[inviter_id])
            return

        inviter_username = self.player_usernames.get(inviter_id, "Someone")
        self.send(Protocols.Response.INVITE_RECEIVED, {
            "inviter_id": inviter_id,
            "inviter_username": inviter_username
        }, self.player_sockets[target_id])
        
        print(f"Player {inviter_id} ({inviter_username}) invited Player {target_id}.")

    def handle_invite_response(self, respondee_id, message):
        inviter_id = message.get("inviter_id")
        accepted = message.get("accepted", False)

        if not inviter_id or inviter_id not in self.player_sockets:
            return # Inviter has disconnected

        if accepted:
            print(f"Player {respondee_id} accepted invite from {inviter_id}.")
            self.send(Protocols.Response.INVITE_ACCEPTED, {"respondee_id": respondee_id}, self.player_sockets[inviter_id])
            time.sleep(0.1) # A small delay to ensure messages are processed
            self.create_direct_game(inviter_id, respondee_id, "1v1")
        else:
            print(f"Player {respondee_id} declined invite from {inviter_id}.")
            self.send(Protocols.Response.INVITE_DECLINED, {"respondee_id": respondee_id}, self.player_sockets[inviter_id])

    BULLET_SPEED = 200

    def update_room_bullets(self, room):
        bullets_to_remove = []
        
        for bullet_id, bullet in list(room.bullets.items()):
            bullet['pos'][0] += bullet['direction'][0] * BULLET_SPEED / 60
            bullet['pos'][1] += bullet['direction'][1] * BULLET_SPEED / 60
            
            for victim_id in room.players:
                if victim_id == bullet['owner_id']:
                    continue
                
                victim_state = room.player_states.get(victim_id)
                if not victim_state or not victim_state.get('pos'):
                    continue
    
                bullet_rect = (bullet['pos'][0], bullet['pos'][1], 10, 10) 
                victim_rect = (victim_state['pos'][0], victim_state['pos'][1], 40, 80)
                
                if check_collision(bullet_rect, victim_rect):
                    print(f"Bullet collision! Bullet from {bullet['owner_id']} hit {victim_id}")
                    if room.player_health[victim_id] > 0:
                        room.player_health[victim_id] -= 1
                        damage_info = {
                            "victim_id": victim_id,
                            "attacker_id": bullet['owner_id'],
                            "new_health": room.player_health[victim_id]
                        }
                        for p_id in room.players:
                            if p_id in self.player_sockets:
                                self.send(Protocols.Response.PLAYER_TOOK_DAMAGE, damage_info, self.player_sockets[p_id])

                    bullets_to_remove.append(bullet_id)
                    break
            
            if bullet['pos'][0] < 0 or bullet['pos'][0] > 1920 or bullet['pos'][1] < 0 or bullet['pos'][1] > 1080:
                bullets_to_remove.append(bullet_id)

        for bullet_id in bullets_to_remove:
            if bullet_id in room.bullets:
                del room.bullets[bullet_id]

 
if __name__ == "__main__":
    server = Server()
    try:
        server.receive()
    except KeyboardInterrupt:
        print("Server stopped by user")
    finally:
        server.server.close()
