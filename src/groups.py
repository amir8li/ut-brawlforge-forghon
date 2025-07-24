import pygame
from pygame.math import Vector2 as vector
from random import choice, randint

from config import *
from src.sprites import Sprite, Cloud
from src.timer import Timer

class AllSprites(pygame.sprite.Group):
    def __init__(self, width, height, clouds, horizon_line, bg_tile=None):
        super().__init__()
        self.display_surf = pygame.display.get_surface()
        self.offset = vector(0, 0)
        self.width = width * TILE_SIZE
        self.height = height * TILE_SIZE
        self.have_sky = not bg_tile
        self.horizon_line = horizon_line

        if bg_tile:
            for col in range(width):
                for row in range(height):
                    x = col * TILE_SIZE
                    y = row * TILE_SIZE
                    Sprite((x, y), bg_tile, self, z=-1)
        else:
            self.large_cloud = clouds["large"]
            self.small_clouds = clouds["small"]
            self.cloud_direction = -1

            self.large_cloud_speed = 50
            self.large_cloud_x = 0
            self.large_cloud_tiles = int(self.width / self.large_cloud.get_width()) + 2
            self.large_cloud_width, self.large_cloud_height = self.large_cloud.get_size()

            self.cloud_timer = Timer(2500, self.create_cloud, True)
            self.cloud_timer.activate()
            for cloud in range(15):
                pos = (randint(0, self.width), randint(0, self.horizon_line))
                surf = choice(self.small_clouds)
                Cloud(pos, surf, self)

    def draw_sky(self):
        self.display_surf.fill("#ddc6a1")
        horizon_pos = self.horizon_line + self.offset.y

        sea_rect = pygame.Rect(0, horizon_pos, self.width, self.height - horizon_pos)
        pygame.draw.rect(self.display_surf, "#92a9ce", sea_rect)
        pygame.draw.line(self.display_surf, "#f5f1de", (0, horizon_pos), (SCREEN_SIZE[0], horizon_pos), 2)

    def draw_large_cloud(self, dt):
        self.large_cloud_x += self.cloud_direction * self.large_cloud_speed * dt
        if self.large_cloud_x <= -self.large_cloud_width:
            self.large_cloud_x = 0
        for i in range(self.large_cloud_tiles):
            left = self.large_cloud_x + i * self.large_cloud_width + self.offset.x
            top = self.horizon_line - self.large_cloud_height + self.offset.y
            self.display_surf.blit(self.large_cloud, (left, top))

    def create_cloud(self):
        pos = (randint(self.width + 500, self.width + 600), randint(0, self.horizon_line))
        surf = choice(self.small_clouds)
        Cloud(pos, surf, self)

    def draw(self, target_pos, dt):
        self.offset.x = -(target_pos[0] - SCREEN_SIZE[0] // 2)
        self.offset.y = -(target_pos[1] - SCREEN_SIZE[1] // 2)

        self.offset.x = max(-(self.width - SCREEN_SIZE[0]), min(0, self.offset.x))
        self.offset.y = max(-(self.height - SCREEN_SIZE[1]), min(0, self.offset.y))

        if self.have_sky:
            self.cloud_timer.update()
            self.draw_sky()
            self.draw_large_cloud(dt)

        for sprite in sorted(self, key=lambda sprite: sprite.z):
            offset_pos = sprite.rect.topleft + self.offset
            self.display_surf.blit(sprite.image, offset_pos)

    def custom_draw(self, player):
        if isinstance(player, list):
            if player:
                avg_pos = vector(0, 0)
                for p in player:
                    avg_pos += vector(p.rect.center)
                avg_pos /= len(player)
            else:
                avg_pos = vector(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
        else:
            avg_pos = vector(player.rect.center) if player else vector(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
        
        self.draw(avg_pos, 1/60)