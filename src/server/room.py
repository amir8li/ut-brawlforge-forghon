import uuid
from datetime import datetime

class Room:
    def __init__(self, players, game_mode="1v1"):
        self.id = str(uuid.uuid4())
        self.players = players
        self.game_mode = game_mode 
        self.bullets = {}
        self.status = "waiting"
        self.created_time = datetime.now()
        self.countdown_start = None
        self.max_players = len(players)
        
        if game_mode == "2v2":
            self.team1 = players[:2]
            self.team2 = players[2:]
        else:
            self.team1 = [players[0]]
            self.team2 = [players[1]]
        
       
        initial_health = 5 
        self.player_health = {player_id: initial_health for player_id in players}
        
        self.player_states = {}
        for player_id in players:
            self.player_states[player_id] = {
                'pos': (0, 0), 
                'face_right': True
            }

class RoomManager:
    def __init__(self):
        self.rooms = {}  
        self.waiting_queue_1v1 = [] 
        self.waiting_queue_2v2 = []   
    
    def add_to_waiting_queue(self, player_id, game_mode="1v1"):
        if game_mode == "1v1":
            queue = self.waiting_queue_1v1
        else:
            queue = self.waiting_queue_2v2
            
        if player_id not in queue:
            queue.append(player_id)
            print(f"Player {player_id} added to {game_mode} waiting queue at position {len(queue)}")
        return len(queue)
    
    def remove_from_waiting_queue(self, player_id):
        removed = False
        if player_id in self.waiting_queue_1v1:
            self.waiting_queue_1v1.remove(player_id)
            print(f"Player {player_id} removed from 1v1 waiting queue")
            removed = True
        if player_id in self.waiting_queue_2v2:
            self.waiting_queue_2v2.remove(player_id)
            print(f"Player {player_id} removed from 2v2 waiting queue")
            removed = True
        return removed
    
    def get_ready_players(self, game_mode="1v1", max_players=None):
        if game_mode == "1v1":
            queue = self.waiting_queue_1v1
            max_players = max_players or 2
        else:
            queue = self.waiting_queue_2v2
            max_players = max_players or 4
            
        if len(queue) >= max_players:
            ready_players = queue[:max_players]
            if game_mode == "1v1":
                self.waiting_queue_1v1 = queue[max_players:]
            else:
                self.waiting_queue_2v2 = queue[max_players:]
            return ready_players
        return []
    
    def create_room(self, player_ids, game_mode="1v1"):
        room_id = str(uuid.uuid4())
        room = Room(player_ids, game_mode)
        
        self.rooms[room_id] = room
        print(f"Created {game_mode} room {room_id} with players: {player_ids}")
        return room_id
    
    def get_room(self, room_id):
        return self.rooms.get(room_id)
    
    def remove_room(self, room_id):
        if room_id in self.rooms:
            del self.rooms[room_id]
            print(f"Removed room {room_id}")
            return True
        return False
    
    def get_player_room(self, player_id):
        for room_id, room in self.rooms.items():
            if player_id in room.players:
                return room_id
        return None
    
    def remove_player_from_room(self, player_id, room_id):
        room = self.rooms.get(room_id)
        if room and player_id in room.players:
            room.players.remove(player_id)
            
            if not room.players:
                self.remove_room(room_id)
            
            print(f"Removed player {player_id} from room {room_id}")
            return True
        return False
    
    def get_room_status(self, room_id):
        room = self.rooms.get(room_id)
        return room.status if room else None
    
    def set_room_status(self, room_id, status):
        room = self.rooms.get(room_id)
        if room:
            room.status = status
            print(f"Room {room_id} status changed to {status}")
            return True
        return False
    
    def get_room_players(self, room_id):
        room = self.rooms.get(room_id)
        return room.players if room else []
    
    
    def get_active_rooms_count(self):
        return len(self.rooms)
    
    def get_room_info(self, room_id):
        room = self.rooms.get(room_id)
        if room:
            return {
                "id": room.id,
                "players": room.players,
                "game_mode": room.game_mode,
                "status": room.status,
                "created_time": room.created_time.isoformat(),
                "countdown_start": room.countdown_start.isoformat() if room.countdown_start else None,
                "max_players": room.max_players,
                "team1": room.team1,
                "team2": room.team2,
                "player_health": room.player_health
            }
        return None
    
    def eliminate_player(self, room_id, player_id):
        room = self.rooms.get(room_id)
        if room and player_id in room.player_health:
            room.player_health[player_id] = 0
            print(f"Player {player_id} eliminated in room {room_id}")
            return True
        return False
    
    def get_player_team(self, room_id, player_id):
        room = self.rooms.get(room_id)
        if room:
            if player_id in room.team1:
                return 1
            elif player_id in room.team2:
                return 2
        return None
    
    def get_team_players(self, room_id, team_number):
        room = self.rooms.get(room_id)
        if room:
            if team_number == 1:
                return room.team1
            elif team_number == 2:
                return room.team2
        return []
    
    def get_waiting_queue_length(self, game_mode="1v1"):
        if game_mode == "1v1":
            return len(self.waiting_queue_1v1)
        else:
            return len(self.waiting_queue_2v2)
