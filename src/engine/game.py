import pygame
import os
import sys

from src.tilemap import Tilemap
from src.entities import Player, Enemy
from src.utils import load_image, load_images
from src.clouds import Clouds

class Game:
    def __init__(self, configs):
        pygame.init()
        self.configs = configs
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((configs.screen_size[0], configs.screen_size[1]))
        self.display = pygame.Surface((configs.screen_size[0]/2, configs.screen_size[1]/2))
        pygame.display.set_caption(configs.caption)

        self.assets = {
            "background": load_images(configs.assets["background"], scale=(configs.screen_size[0]/2, configs.screen_size[1]/2)),
            "grass": load_images(configs.assets["grass"]),
            "dirt": load_images(configs.assets["dirt"]),
            "stone": load_images(configs.assets["stone"]),
            "decor": load_images(configs.assets["decor"]),
            "large_decor": load_images(configs.assets["large_decor"]),
            "player": load_image(configs.assets["player"]),
            "clouds": load_images(configs.assets["clouds"]),
            "enemy": load_image(configs.assets["enemy"])
        }

        self.movement = [False, False]
        self.space_held = False
        self.player = Player(self, configs.spawn_pos, configs.player_size)
        self.enemy = Enemy(self, configs.enemy_spawn_pos, configs.enemy_size)

        self.clouds = Clouds(self.assets["clouds"], count=16)
        self.tilemap = Tilemap(self, tile_size=configs.tile_size)

        self.scroll = [0, 0]

    def run(self):
        running = True
        while running:
            self.clock.tick(self.configs.FPS)
            for layer in self.assets["background"]:
                self.display.blit(layer, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        self.space_held = True
                        if self.player.jump_count < self.configs.max_jump_count:
                            self.player.velocity[1] = -1 * self.configs.jump_velocity
                            self.player.jump_count += 1

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_SPACE:
                        self.space_held = False
                        

            self.scroll[0] += int(self.player.rect().centerx - self.display.get_width() // 2 - self.scroll[0])
            self.scroll[1] += int(self.player.rect().centery - self.display.get_height() // 2 - self.scroll[1])

            self.clouds.update()
            self.clouds.render(self.display, offset=self.scroll)

            self.tilemap.render(self.display, offset=self.scroll)

            self.player.update(self.tilemap, ((self.movement[1] - self.movement[0])*self.configs.movement_speed, 0))
            self.player.render(self.display, offset=self.scroll)

            self.enemy.render(self.display, offset=self.scroll)
            self.enemy.update(self.tilemap, (0, 0))

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
        pygame.quit()