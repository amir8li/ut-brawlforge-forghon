import pygame

from config import *
from src.timer import Timer

class Tooth(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.z = ZLAYERS["main"]

        self.direction = 1
        self.speed = ENEMY_SPEED
        self.collision_rects = [sprite.rect for sprite in collision_sprites]

        self.hit_timer = Timer(350)
        self.name = "Tooth"
        # Font for name display
        self.font = pygame.font.Font(None, 24)
        self.name_surface = self.font.render(self.name, True, (0, 0, 0))  # Black text
        self.name_rect = self.name_surface.get_rect()

    def reverse(self):
        if not self.hit_timer.active:
            self.direction *= -1
            self.hit_timer.activate()

    def draw_name(self, display_surface, offset):
        # Position the name above the enemy's head
        name_x = self.rect.centerx - self.name_rect.width // 2 + offset[0]
        name_y = self.rect.top - 25 + offset[1]  # 25 pixels above the enemy
        self.name_rect.topleft = (name_x, name_y)
        
        # Draw a rounded semi-transparent background for better readability
        bg_rect = self.name_rect.inflate(8, 4)  # Add some padding
        
        # Create a temporary surface for the rounded rectangle
        temp_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, (255, 255, 255, 200), temp_surface.get_rect(), border_radius=6)  # White background
        display_surface.blit(temp_surface, bg_rect)
        
        # Draw the name text
        display_surface.blit(self.name_surface, self.name_rect)

    def update(self, dt):
        self.hit_timer.update()

        # animation
        self.frame_index += 6 * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

        # movement
        self.rect.x += self.direction * self.speed * dt

        # reverse direction
        floor_rect_right = pygame.Rect(self.rect.bottomright, (1, 1))
        floor_rect_left = pygame.Rect(self.rect.bottomleft, (-1, 1))
        rect_right = pygame.Rect(self.rect.bottomright, (1, -1))
        rect_left = pygame.Rect(self.rect.bottomleft, (-1, -1))

        if floor_rect_right.collidelist(self.collision_rects) < 0 and self.direction > 0:
            self.direction = -1
        elif floor_rect_left.collidelist(self.collision_rects) < 0 and self.direction < 0:
            self.direction = 1
        elif rect_right.collidelist(self.collision_rects) > 0 and self.direction > 0:
            self.direction = -1
        elif rect_left.collidelist(self.collision_rects) > 0 and self.direction < 0:
            self.direction = 1
