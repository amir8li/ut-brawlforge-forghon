import pygame
import sys
from pytmx.util_pygame import load_pygame

from src.utils import *
from src.level import Level

class Game:
    def __init__(self, configs):
        pygame.init()
        self.configs = configs
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((configs.screen_size[0], configs.screen_size[1]))
        self.import_assets()
        pygame.display.set_caption(configs.caption)

        self.tmx_maps = {0: load_pygame("./data/levels/omni.tmx")}

        self.current_stage = Level(self.tmx_maps[0], self.level_frames, configs)

    def import_assets(self):
        self.level_frames = {
            "flag": import_folder("graphics", "level", "flag"),
            "saw": import_folder("graphics", "enemies", "saw", "animation"),
            "floor_spike": import_folder("graphics", "enemies", "floor_spikes"),
            "candle": import_folder("graphics", "level", "candle"),
            "window": import_folder("graphics", "level", "window"),
            "big_chain": import_folder("graphics", "level", "big_chains"),
            "small_chain": import_folder("graphics", "level", "small_chains"),
            "candle_light": import_folder("graphics", "level", "candle light"),
            "player": import_sub_folders("graphics", "player"),
            "helicopter": import_folder("graphics", "level", "helicopter"),
            "boat": import_folder("graphics", "objects", "boat"),
            "saw_chain": import_image("graphics", "enemies", "saw", "saw_chain"),
            "spike": import_image("graphics", "enemies", "spike_ball", "Spiked Ball"),
            "spike_chain": import_image("graphics", "enemies", "spike_ball", "spiked_chain"),
            "tooth": import_folder("graphics", "enemies", "tooth", "run"),
            "palms": import_sub_folders("graphics", "level", "palms"),
            "water_top": import_folder("graphics", "level", "water", "top"),
            "water_body": import_image("graphics", "level", "water", "body"),
            "items": import_sub_folders("graphics", "items"),
            "particle": import_folder("graphics", "effects", "particle")
        }
    def run(self):
        running = True
        while running:
            self.screen.fill("black")
            dt = self.clock.tick(self.configs.FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

            self.current_stage.run(dt)
            pygame.display.flip()