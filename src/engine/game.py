import pygame
import sys
from pytmx.util_pygame import load_pygame
from config import *
from src.utils import *
from src.level import Level

class Game:
    def __init__(self, mode=None, selected_map=None, selected_hero=None, player_names=None):
        pygame.init()
        self.mode = mode
        self.selected_map = selected_map
        self.selected_hero = selected_hero
        self.player_names = player_names

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption(CAPTION)

        self.import_assets()

        if self.mode == "multi" and self.player_names and len(self.player_names) >= 2:
            names = {0: self.player_names[0], 1: self.player_names[1]}
        else:
            names = None

        self.ui = UI(self.font, self.ui_frames, self.mode, player_names=names)

        self.data = [Data(self.ui, i) for i in range(2 if self.mode == "multi" else 1)]
        if self.mode == "multi":
            for i, data in enumerate(self.data):
                data.name = self.player_names[i]
                data.character = self.selected_hero[i]
        else:
            self.data[0].name = self.player_names[0]
            self.data[0].character = self.selected_hero

        self.tmx_maps = {0: load_pygame(join("data", "levels", self.selected_map))}
        self.current_stage = Level(
            self.tmx_maps[0],
            self.level_frames,
            self.audio_files,
            self.data,
            self.powerup_locations 
        )


        self.bg_sound = self.audio_files['bg']
        self.bg_sound.set_volume(0.3)
        self.bg_sound.play(-1)

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
            "palms": import_sub_folders("src", "assets", "images", "level", "palms"),
            "water_top": import_folder("src", "assets", "images", "level", "water", "top"),
            "water_body": import_image("src", "assets", "images", "level", "water", "body"),
            "items": import_sub_folders("src", "assets", "images", "items"),
            "particle": import_folder("src", "assets", "images", "effects", "particle"),
            "bg_tiles": import_folder_dict("src", "assets", "images", "level", "bg", "tiles"),
            "cloud_small": import_folder("src", "assets", "images", "level", "clouds", "small"),
            "cloud_large": import_image("src", "assets", "images", "level", "clouds", "large_cloud"),
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
                "double_jump": [(600, 480)],
                "magic": [(800, 360)],
                "shield": [(720, 300)]
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
            'attack': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'attack.wav')),
            'coin': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'coin.wav')),
            'jump': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'jump.wav')),
            'damage': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'damage.wav')),
            'bullet': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'bullet.wav')),
            'bg': pygame.mixer.Sound(join('src', 'assets', 'sounds', 'starlight_city.mp3'))
        }

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

            self.current_stage.update(dt)
            self.screen.fill("#91a7d0")
            self.current_stage.draw(self.screen)
            self.ui.update(dt)
            pygame.display.flip()

            result = self.current_stage.check_constraint()

            if result in ["win", "gameover"] or (result is not None and result.endswith("won")):
                self.bg_sound.stop()
                return result