import pygame
from pygame.math import Vector2 as vector

from src.sprites import Sprite

class AllSprites(pygame.sprite.Group):
    def __init__(self, width, height, bg_tile=None):
        super().__init__()
        self.display_surf = pygame.display.get_surface()
        self.offset = vector(0, 0)
        self.width = width * 64
        self.height = height * 64

        if bg_tile:
            for col in range(width):
                for row in range(height):
                    x = col * 64
                    y = row * 64
                    Sprite((x, y), bg_tile, self, z=-1)
                    
    
    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - 640)
        self.offset.y = -(target_pos[1] - 360)
        
        # Clamp camera to level bounds
        self.offset.x = max(-(self.width - 1280), min(0, self.offset.x))
        self.offset.y = max(-(self.height - 720), min(0, self.offset.y))
        
        for sprite in sorted(self, key = lambda sprite: sprite.z):
            offset_pos = sprite.rect.topleft + self.offset
            self.display_surf.blit(sprite.image, offset_pos)