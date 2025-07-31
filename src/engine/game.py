import pygame
import sys
import json
from pytmx.util_pygame import load_pygame
from config import *
from src.level import Level
from src.utils import *

class Game:
    def __init__(self, mode=None, selected_map=None, selected_hero=None, player_names=None, screen=None, audio_files=None, settings=None, current_level=1):
        pygame.init()
        self.screen = screen
        self.audio_files = audio_files
        self.settings = settings
        self.mode = mode
        self.selected_map = selected_map
        self.selected_hero = selected_hero
        self.player_names = player_names
        self.clock = pygame.time.Clock()
        
        if self.screen is None:
            self.screen = pygame.display.set_mode(SCREEN_SIZE)
            pygame.display.set_caption(CAPTION)
        
        if self.settings is None:
            self.settings = self.load_settings()
        
        self.music_volume = self.settings.get("music_volume", 0.5)
        
        if self.audio_files is None:
            self.audio_files, _ = self.load_audio_files(self.settings)

        self.boss_sequence_requested = False
        self.current_level_num = current_level

      
        if self.mode and self.selected_map and self.selected_hero:
            self.import_assets()
            
            if self.mode == "multi" and self.player_names and len(self.player_names) >= 2:
                names = {i: name for i, name in enumerate(self.player_names)}
            else:
                names = {0: self.player_names[0]} if self.player_names else None
            
            self.ui = UI(self.font, self.ui_frames, self.mode, player_names=names, audio_files=self.audio_files)
            self.data = [Data(self.ui, i) for i in range(2 if self.mode == "multi" else 1)]
            
            if self.mode == "multi":
                for i, data in enumerate(self.data):
                    data.name = self.player_names[i]
                    data.character = self.selected_hero[i]
            else:
                self.data[0].name = self.player_names[0]
                self.data[0].character = self.selected_hero

            tmx_map = load_pygame(self.selected_map)
            
            self.current_stage = Level(
                tmx_map,
                self.level_frames,
                self.audio_files,
                self.data,
                self.font,
                game=self,
                powerup_locations=self.powerup_locations,
                current_level=self.current_level_num
            )
            
            self.bg_sound = self.audio_files.get('bg')
            if self.bg_sound:
                self.bg_sound.set_volume(self.music_volume)
                self.bg_sound.play(-1)

        # # Always pass player_names as a dict to UI
        # # (Removed duplicate UI creation to fix heart display)
        # self.tmx_maps = {
        #     "boss": load_pygame("./data/levels/boss 5.tmx")
        # }
        self.boss_maps = [
            "boss 1.tmx",
            "boss 2.tmx",
            "boss 3.tmx",
            "boss 4.tmx",
            "boss 5.tmx",
        ]
        self.current_boss_index = 0
        self.tmx_maps = {
            name: load_pygame(f"./data/levels/{name}") for name in self.boss_maps
        }

    def request_boss_sequence(self):
            """این متد توسط Level.start_boss_fight فراخوانی می‌شود"""
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
            'type': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'type.wav'))
        }
        for key in ['bg', 'menu_bg']:
            audio_files[key].set_volume(music_volume)
        for key in ['attack', 'coin', 'jump', 'damage', 'bullet', 'click', 'transition', 'loading', 'win', 'gameover', 'type']:
            audio_files[key].set_volume(sfx_volume)
        return audio_files, settings

    def import_assets(self):
        if self.mode == "multi":
            self.player_frames = [import_character_frames("src", "assets", "images", "players", hero) for hero in self.selected_hero]
        else:
            self.player_frames = import_character_frames("src", "assets", "images", "players", self.selected_hero)
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
            "6.tmx": {
                "double_jump": [(200, 550), (600, 400), (1000, 300)],
                "magic": [(300, 150), (800, 180)],
                "shield": [(150, 350), (650, 200)]
            },
            "3.tmx": {
                "double_jump": [(180, 480), (500, 440)],
                "magic": [(350, 300), (850, 280)],
                "shield": [(250, 200), (720, 220)]
            },
            "4.tmx": {
                "double_jump": [(960, 1344), (576, 1472)],
                "magic": [(832, 960), (640, 1408)],
                "shield": [(960, 1344)]
            },
            "7.tmx": {
                "double_jump": [(240, 380), (800, 360)],
                "magic": [(400, 240), (1000, 220)],
                "shield": [(150, 140), (650, 120)]
            }
        }
        self.ui_frames = {
            "heart": import_folder("src", "assets", "images", "ui", "heart"),
            "coin": import_image("src", "assets", "images", "ui", "coin"),
        }
        self.font = pygame.font.Font(join("src", "assets", "images", "ui", "runescape_uf.ttf"), 40)

        self.audio_files = {
            'attack':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'attack.wav')),
            'coin':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'coin.wav')),
            'jump':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'jump.wav')),
            'damage':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'damage.wav')),
            'bullet':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'bullet.wav')),
            'bg':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'starlight_city.mp3')),
            'bombastic_explosion':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'bombastic explosion.wav')),
            'bombastic_death':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'bombastic death.wav')),
            'archer_death':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'archer death.mp3')),
            'archer_wizard_damage':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'archer wizard damage.wav')),
            'wizard_death':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'wizard death.wav')),
            'tooth_death':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'tooth death.wav')),
            'tooth_damage':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'tooth damage.wav'))
        }
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.bg_sound.stop()
                    pygame.quit()
                    sys.exit()

            if self.boss_sequence_requested:
                self.bg_sound.stop()
                return "start_boss_sequence"

            self.current_stage.handle_events(events)
            self.current_stage.update(dt)
            
            self.screen.fill("#91a7d0")
            self.current_stage.draw(self.screen)
            self.ui.update(dt)
            pygame.display.flip()

            result = self.current_stage.check_constraint()
            if result: 
                self.bg_sound.stop()
                return result

    