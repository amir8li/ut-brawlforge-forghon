import pygame
import sys
from pytmx.util_pygame import load_pygame

from config import *
from src.utils import *
from src.level import Level

class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.import_assets()
        pygame.display.set_caption(CAPTION)

        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)
        self.tmx_maps = {0: load_pygame("./data/levels/omni.tmx")}

        self.current_stage = Level(self.tmx_maps[0], self.level_frames, self.audio_files, self.data)
        
        self.bg_sound = self.audio_files['bg']
        self.bg_sound.set_volume(0.3)
        self.bg_sound.play(-1)

    def import_assets(self):
        self.level_frames = {
            "flag": import_folder("src", "assets", "images", "level", "flag"),
            "saw": import_folder("src", "assets", "images", "enemies", "saw", "animation"),
            "floor_spike": import_folder("src", "assets", "images", "enemies", "floor_spikes"),
            "candle": import_folder("src", "assets", "images", "level", "candle"),
            "window": import_folder("src", "assets", "images", "level", "window"),
            "big_chain": import_folder("src", "assets", "images", "level", "big_chains"),
            "small_chain": import_folder("src", "assets", "images", "level", "small_chains"),
            "candle_light": import_folder("src", "assets", "images", "level", "candle light"),
            "player": import_sub_folders("src", "assets", "images", "player"),
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
            'archer_damage':pygame.mixer.Sound(join('src', 'assets', 'sounds', 'archer damage.wav'))
        }
    def run(self):
        running = True
        while running:
            self.screen.fill("black")
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

            self.current_stage.run(dt)
            self.ui.update(dt)
            pygame.display.flip()