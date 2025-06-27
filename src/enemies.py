import pygame
from src.timer import Timer

class Tooth(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.z = 5

        self.direction = 1
        self.speed = 200
        self.collision_rects = [sprite.rect for sprite in collision_sprites]

        self.hit_timer = Timer(350)

    def reverse(self):
        if not self.hit_timer.active:
            self.direction *= -1
            self.hit_timer.activate()

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