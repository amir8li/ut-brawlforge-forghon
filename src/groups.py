import pygame
from pygame.math import Vector2 as vector

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surf = pygame.display.get_surface()
        self.offset = vector(0, 0)
    
    def draw(self, target_pos):
        self.offset.x = 640 - target_pos[0]
        self.offset.y = 360 - target_pos[1]
        for sprite in sorted(self, key = lambda sprite: sprite.z):
            offset_pos = sprite.rect.topleft + self.offset
            self.display_surf.blit(sprite.image, offset_pos)