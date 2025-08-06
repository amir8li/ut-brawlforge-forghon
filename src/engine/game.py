import pygame
import sys
import json
from pytmx.util_pygame import load_pygame
from config import *
from src.level import Level
from src.utils import *

class Game:
    def __init__(self, mode=None, selected_map=None, selected_hero=None, player_names=None, screen=None, audio_files=None, settings=None, current_level=1, network=None, online_game_data=None):
        print("DEBUG: Game.__init__ started.")
        pygame.init()
        self.screen = screen if screen is not None else pygame.display.set_mode(SCREEN_SIZE)
        self.settings = settings if settings is not None else self.load_settings()
        self.audio_files = audio_files if audio_files is not None else self.load_audio_files(self.settings)[0]
        
        self.mode = mode
        self.selected_map = selected_map
        self.selected_hero = selected_hero
        self.player_names = player_names
        self.clock = pygame.time.Clock()
        self.network = network
        self.online_game_data = online_game_data
        
        self.music_volume = self.settings.get("music_volume", 0.5)
        self.boss_sequence_requested = False
        self.current_level_num = current_level

        if self.mode and self.selected_map and self.selected_hero is not None:
            self.setup_game()
        print("DEBUG: Game.__init__ finished.")
                
    def setup_game(self):
            print("DEBUG: Game.setup_game started.")
            self.import_assets()
            
            num_players = 0
            player_names_dict = {}

            if self.mode == 'online':
                num_players = len(self.online_game_data['players'])
                player_names_dict = {0: self.player_names[0]}
                for i in range(1, num_players):
                    player_names_dict[i] = f"Opponent {i}"
            elif self.mode == 'multi':
                num_players = len(self.player_names)
                player_names_dict = {i: name for i, name in enumerate(self.player_names)}
            else:
                num_players = 1
                player_names_dict = {0: self.player_names[0]}

            self.ui = UI(self.font, self.ui_frames, self.mode, player_names=player_names_dict, audio_files=self.audio_files)
            self.data = [Data(self.ui, i) for i in range(num_players)]

            for i, data_obj in enumerate(self.data):
                data_obj.name = player_names_dict[i]
                if isinstance(self.selected_hero, list):
                    data_obj.character = self.selected_hero[i]
                else:
                    data_obj.character = self.selected_hero
            
            tmx_map = load_pygame(self.selected_map)
            
            self.current_stage = Level(
                tmx_map, self.level_frames, self.audio_files, self.data, self.font,
                game=self, powerup_locations=getattr(self, 'powerup_locations', {}),
                current_level=self.current_level_num
            )
            
            self.bg_sound = self.audio_files.get('bg')
            if self.bg_sound:
                self.bg_sound.set_volume(self.music_volume)
                self.bg_sound.play(-1)
            print("DEBUG: Game.setup_game finished.")

    def request_boss_sequence(self):
        self.boss_sequence_requested = True

    @staticmethod
    def load_settings():
        try:
            with open("settings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"music_volume": 0.5, "sfx_volume": 0.7}

    @staticmethod
    def load_audio_files(settings):
        music_volume = settings.get("music_volume", 0.5)
        sfx_volume = settings.get("sfx_volume", 0.7)
        audio_files = {
            'attack': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'attack.wav')),
            'coin': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'coin.wav')),
            'jump': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'jump.wav')),
            'damage': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'damage.wav')),
            'bullet': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'bullet.wav')),
            'bg': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'starlight_city.mp3')),
            'click': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'click.wav')),
            'transition': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'transition.wav')),
            'loading': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'loading.wav')),
            'menu_bg': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'menu_bg.wav')),
            'win': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'win.wav')),
            'gameover': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'gameover.wav')),
            'type': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'type.wav')),
            'bombastic_explosion':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'bombastic explosion.wav')),
            'bombastic_death':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'bombastic death.wav')),
            'archer_death':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'archer death.mp3')),
            'archer_wizard_damage':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'archer wizard damage.wav')),
            'wizard_death':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'wizard death.wav')),
            'tooth_death':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'tooth death.wav')),
            'tooth_damage':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'tooth damage.wav'))
        }
        for key in ['bg', 'menu_bg']:
            if key in audio_files: audio_files[key].set_volume(music_volume)
        for key in audio_files:
            if key not in ['bg', 'menu_bg']: audio_files[key].set_volume(sfx_volume)
        return audio_files, settings

    def import_assets(self):
        print("DEBUG: Game.import_assets started.")
        self.player_frames = []
        if isinstance(self.selected_hero, list):
            for hero_id in self.selected_hero:
                frames = import_character_frames("src", "assets", "images", "players", hero_id)
                self.player_frames.append(frames)
        else:
            frames = import_character_frames("src", "assets", "images", "players", self.selected_hero)
            self.player_frames.append(frames)
        
        self.level_frames = {
            "flag": import_folder("src", "assets", "images", "level", "flag"),
            "saw": import_folder("src", "assets", "images", "enemies", "saw", "animation"),
            "floor_spike": import_folder("src", "assets", "images", "enemies", "floor_spikes"),
            "candle": import_folder("src", "assets", "images", "level", "candle"),
            "window": import_folder("src", "assets", "images", "level", "window"),
            "big_chain": import_folder("src", "assets", "images", "level", "big_chains"),
            "small_chain": import_folder("src", "assets", "images", "level", "small_chains"),
            "candle_light": import_folder("src", "assets", "images", "level", "candle light"),
            "player": self.player_frames,
            "helicopter": import_folder("src", "assets", "images", "level", "helicopter"),
            "boat": import_folder("src", "assets", "images", "objects", "boat"),
            "saw_chain": import_image("src", "assets", "images", "enemies", "saw", "saw_chain"),
            "spike": import_image("src", "assets", "images", "enemies", "spike_ball", "Spiked Ball"),
            "spike_chain": import_image("src", "assets", "images", "enemies", "spike_ball", "spiked_chain"),
            "tooth": import_folder("src", "assets", "images", "enemies", "tooth", "run"),
            "bombastic": import_folder("src", "assets", "images", "enemies", "bombastic", "Moving"),
            "bombastic_explosion": import_folder("src", "assets", "images", "enemies", "bombastic", "Explosion"),
            "bombastic_dead": import_folder("src", "assets", "images", "enemies", "bombastic", "Dead"),
            "palms": import_sub_folders("src", "assets", "images", "level", "palms"),
            "water_top": import_folder("src", "assets", "images", "level", "water", "top"),
            "water_body": import_image("src", "assets", "images", "level", "water", "body"),
            "items": import_sub_folders("src", "assets", "images", "items"),
            "particle": import_folder("src", "assets", "images", "effects", "particle"),
            "bg_tiles": import_folder_dict("src", "assets", "images", "level", "bg", "tiles"),
            "cloud_small": import_folder("src", "assets", "images", "level", "clouds", "small"),
            "cloud_large": import_image("src", "assets", "images", "level", "clouds", "large_cloud"),
            "archer": import_sub_folders("src", "assets", "images", "enemies", "archer"),
            "ice_wizard": import_sub_folders("src", "assets", "images", "enemies", "ice wizard"),
            "powerups": {
                "double_jump": import_image("src", "assets", "images", "powerup", "double_jump"),
                "magic": import_image("src", "assets", "images", "powerup", "magic"),
                "shield": import_image("src", "assets", "images", "powerup", "shield"),
            },
        }
        self.powerup_locations = {
             "6.tmx": { "double_jump": [(200, 550), (600, 400), (1000, 300)], "magic": [(300, 150), (800, 180)], "shield": [(150, 350), (650, 200)] },
             "3.tmx": { "double_jump": [(180, 480), (500, 440)], "magic": [(350, 300), (850, 280)], "shield": [(250, 200), (720, 220)] },
             "4.tmx": { "double_jump": [(960, 1344), (576, 1472)], "magic": [(832, 960), (640, 1408)], "shield": [(960, 1344)] },
             "7.tmx": { "double_jump": [(240, 380), (800, 360)], "magic": [(400, 240), (1000, 220)], "shield": [(150, 140), (650, 120)] }
        }
            
        self.ui_frames = {
            "heart": import_folder("src", "assets", "images", "ui", "heart"),
            "coin": import_image("src", "assets", "images", "ui", "coin"),
        }
        self.font = pygame.font.Font(join("src", "assets", "images", "ui", "runescape_uf.ttf"), 40)
# در فایل src/engine/game.py، داخل کلاس Game
        print("DEBUG: Game.import_assets finished.")

    def run(self):
        print("DEBUG: Game.run started.") 
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000
            dt = min(dt, 0.1)
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    if self.network: self.network.disconnect()
                    if self.bg_sound: self.bg_sound.stop()
                    pygame.quit()
                    sys.exit()

            # --- این بلوک کد اصلاح شده و بازگردانده شده است ---
            if self.boss_sequence_requested:
                if self.bg_sound: self.bg_sound.stop()
                return "start_boss_sequence"
            # --- پایان بخش اصلاح شده ---

            if self.mode == 'online' and self.network:
                local_player = self.current_stage.get_local_player()
                if local_player:
                    packet = { "type": "game_action", "action": "player_update", "data": { 'pos': list(local_player.hitbox_rect.topleft), 'state': local_player.state, 'face_right': local_player.face_right, 'health': local_player.data.health }}
                    self.network.send(packet)

                server_msg = self.network.get_message()
                while server_msg:
                    if server_msg.get('type') == 'game_action':
                        data = server_msg.get('data', {})
                        sender_id = data.get('player_id')
                        all_ids = self.online_game_data['players']
                        if sender_id and sender_id in all_ids:
                            try:
                                p_index = all_ids.index(sender_id)
                                remote_player = self.current_stage.players[p_index]
                                if data.get('action') == 'player_update':
                                    remote_player.update_from_network(data.get('data', {}))
                            except (ValueError, IndexError): pass
                    server_msg = self.network.get_message()

            self.current_stage.update(dt) # آپدیت مرحله بعد از شبکه
            self.current_stage.handle_events(events) # هندل کردن ایونت‌ها
            
            self.screen.fill("#91a7d0")
            self.current_stage.draw(self.screen)
            self.ui.update(dt)
            pygame.display.flip()

            result = self.current_stage.check_constraint()
            if result: 
                if self.bg_sound: self.bg_sound.stop()
                return result