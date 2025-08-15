from mongoengine import connect, Document, StringField, IntField, DateTimeField, BooleanField
from datetime import datetime

class Player(Document):
    """MongoDB model for storing player data"""
    player_id = StringField(required=True, unique=True)
    username = StringField(required=True, max_length=50)
    level = IntField(default=1)
    score = IntField(default=0)
    games_played = IntField(default=0)
    games_won = IntField(default=0)
    is_online = BooleanField(default=False)
    last_login = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'players',
        'indexes': ['player_id', 'username']
    }
    
    def to_dict(self):
        """Convert player document to dictionary"""
        return {
            'player_id': self.player_id,
            'username': self.username,
            'level': self.level,
            'score': self.score,
            'games_played': self.games_played,
            'games_won': self.games_won,
            'is_online': self.is_online,
            'last_login': self.last_login,
            'created_at': self.created_at
        }

class GameSession(Document):
    """MongoDB model for storing game session data"""
    session_id = StringField(required=True, unique=True)
    room_id = StringField(required=True)
    players = StringField()  # JSON string of player IDs
    started_at = DateTimeField(default=datetime.utcnow)
    ended_at = DateTimeField()
    winner = StringField()
    game_duration = IntField()  # in seconds
    
    meta = {
        'collection': 'game_sessions',
        'indexes': ['session_id', 'room_id']
    }

class DB:
    def __init__(self, db_name='brawlforge_game'):
        print("[DB] INIT START - DEBUG OUTPUT")
        import os
        
        # Use MONGO_URI environment variable
        mongo_uri = os.getenv('MONGO_URI')
        
        if mongo_uri:
            print(f"[DB] Using MONGO_URI: {mongo_uri}")
            connect(host=mongo_uri)
            print(f"[DB] Connected to MongoDB using URI")
        else:
            # Fallback to localhost if no URI provided
            print("[DB] No MONGO_URI found, using localhost fallback")
            connect(db_name, host='localhost', port=27017)
            print(f"[DB] Connected to MongoDB: {db_name} at localhost:27017")
        
        print("[DB] INIT END - DEBUG OUTPUT")
    
    def create_player(self, player_id, username):
        """Create a new player in the database"""
        try:
            player = Player(
                player_id=player_id,
                username=username
            )
            player.save()
            return player
        except Exception as e:
            print(f"Error creating player: {e}")
            return None
    
    def get_player(self, player_id):
        """Get player by ID"""
        try:
            return Player.objects(player_id=player_id).first()
        except Exception as e:
            print(f"Error getting player: {e}")
            return None
    
    def get_player_by_username(self, username):
        """Get player by username"""
        try:
            return Player.objects(username=username).first()
        except Exception as e:
            print(f"Error getting player by username: {e}")
            return None
    
    def update_player_status(self, player_id, is_online=True):
        """Update player online status"""
        try:
            player = Player.objects(player_id=player_id).first()
            if player:
                player.is_online = is_online
                if is_online:
                    player.last_login = datetime.utcnow()
                player.save()
                return True
            return False
        except Exception as e:
            print(f"Error updating player status: {e}")
            return False
    
    def update_player_stats(self, player_id, score_increase=0, game_won=False):
        """Update player game statistics"""
        try:
            player = Player.objects(player_id=player_id).first()
            if player:
                player.score += score_increase
                player.games_played += 1
                if game_won:
                    player.games_won += 1
                player.save()
                return True
            return False
        except Exception as e:
            print(f"Error updating player stats: {e}")
            return False
    
    def get_online_players(self):
        """Get all currently online players"""
        try:
            return Player.objects(is_online=True)
        except Exception as e:
            print(f"Error getting online players: {e}")
            return []
    
    def create_game_session(self, session_id, room_id, players):
        """Create a new game session"""
        try:
            import json
            session = GameSession(
                session_id=session_id,
                room_id=room_id,
                players=json.dumps(players)
            )
            session.save()
            return session
        except Exception as e:
            print(f"Error creating game session: {e}")
            return None
    
    def end_game_session(self, session_id, winner=None):
        """End a game session"""
        try:
            session = GameSession.objects(session_id=session_id).first()
            if session:
                session.ended_at = datetime.utcnow()
                session.winner = winner
                if session.started_at:
                    duration = (session.ended_at - session.started_at).total_seconds()
                    session.game_duration = int(duration)
                session.save()
                return True
            return False
        except Exception as e:
            print(f"Error ending game session: {e}")
            return False