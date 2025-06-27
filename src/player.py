import pygame
from pygame.math import Vector2 as vector
from math import sin

from src.timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, semi_collision_sprites, frames, data):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.state = "idle"
        self.face_right = True
        self.image = self.frames[self.state][self.frame_index]
        self.z = 5
        self.data = data
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox_rect = self.rect.inflate(-76, -36)
        self.old_rect = self.hitbox_rect.copy()

        # movement
        self.direction = vector(0, 0)
        self.speed = 5
        self.gravity = 1300
        self.jump = False
        self.jump_height = -600
        self.attacking = False

        # cayote_time
        self.cayote_time = 0.1
        self.cayote_timer = 0

        # collision
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.on_surface = {'left': False, 'right': False, 'top': False, 'floor': False}
        self.platform = None

        self.timers = {
            "wall_jump": Timer(500),
            "wall_slide": Timer(250),
            "platform_skip": Timer(100),
            "attack_cooldown": Timer(500),
            "hit": Timer(400),
        }

    def input(self):
        keys = pygame.key.get_pressed()
        input_vector = vector(0, 0)

        if not self.timers["wall_jump"].active:
            if keys[pygame.K_d]:
                input_vector.x += 1
                self.face_right = True
            if keys[pygame.K_a]:
                input_vector.x -= 1
                self.face_right = False
            if keys[pygame.K_s]:
                self.timers["platform_skip"].activate()

            # left click
            if pygame.mouse.get_pressed()[0]:
                self.attack()

            self.direction.x = input_vector.normalize().x if input_vector else input_vector.x

        if keys[pygame.K_SPACE]:
            self.jump = True

    def attack(self):
        if not self.timers["attack_cooldown"].active:
            self.attacking = True
            self.frame_index = 0
            self.timers["attack_cooldown"].activate()

    def move(self, dt):
        self.hitbox_rect.x += self.direction.x * self.speed
        self.collision('horizontal')

        if not self.on_surface['floor'] and any((self.on_surface['left'], self.on_surface['right'])) and not self.timers["wall_slide"].active:
            self.direction.y = 0
            self.hitbox_rect.y += self.gravity / 10 * dt
        else:
            self.direction.y += self.gravity / 2 * dt
            self.hitbox_rect.y += self.direction.y * dt
            self.direction.y += self.gravity / 2 * dt
        
        if self.jump:
            if self.on_surface['floor']:
                self.direction.y = self.jump_height
                self.timers["wall_slide"].activate()
                self.hitbox_rect.bottom -= 1
            elif any((self.on_surface['left'], self.on_surface['right'])) and not self.timers["wall_slide"].active:
                self.timers["wall_jump"].activate()
                self.direction.y = self.jump_height
                self.direction.x = 0.5 if self.on_surface['left'] else -0.5
            self.jump = False

        self.collision('vertical')
        self.semi_collision()
        self.rect.center = self.hitbox_rect.center

    def platform_move(self, dt):
        if self.platform:
            self.hitbox_rect.topleft += self.platform.direction * self.platform.speed * dt

    def check_contact(self):
        floor_rect = pygame.Rect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 2))
        right_rect = pygame.Rect(self.hitbox_rect.topright + vector(0, self.hitbox_rect.height / 4), (2, self.hitbox_rect.height / 2))
        left_rect = pygame.Rect(self.hitbox_rect.topleft + vector(-2, self.hitbox_rect.height / 4), (2, self.hitbox_rect.height / 2))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        semi_collide_rects = [sprite.rect for sprite in self.semi_collision_sprites]

        self.on_surface['floor'] =  True if floor_rect.collidelist(collide_rects) >= 0 or floor_rect.collidelist(semi_collide_rects) >= 0 and self.direction.y >= 0 else False
        self.on_surface['right'] = True if right_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface['left']  = True if left_rect.collidelist(collide_rects) >= 0 else False

        self.platform = None
        sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
        for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
            if sprite.rect.colliderect(floor_rect):
                self.platform = sprite

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == 'horizontal':
                    if self.hitbox_rect.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.old_rect.right):
                        self.hitbox_rect.left = sprite.rect.right
                    if self.hitbox_rect.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.old_rect.left):
                        self.hitbox_rect.right = sprite.rect.left
                else:
                    if self.hitbox_rect.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.old_rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom
                        if hasattr(sprite, 'moving'):
                            self.hitbox_rect.top += 6
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                    self.direction.y = 0

    def semi_collision(self):
        if not self.timers["platform_skip"].active:
            for sprite in self.semi_collision_sprites:
                if sprite.rect.colliderect(self.hitbox_rect):
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                        if self.direction.y > 0:
                            self.direction.y = 0

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def animate(self, dt):
        self.frame_index += 6 * dt
        if self.state == "attack" and self.frame_index >= len(self.frames[self.state]):
            self.state = "idle"
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]
        self.image = pygame.transform.flip(self.image, not self.face_right, False)

        if self.attacking and self.frame_index > len(self.frames[self.state]):
            self.attacking = False

    def get_state(self):
        if self.on_surface['floor']:
            if self.attacking:
                self.state = "attack"
            elif self.direction.x != 0:
                self.state = "run"
            else:
                self.state = "idle"
        else:
            if self.attacking:
                self.state = "air_attack"
            else:
                if self.on_surface['left'] or self.on_surface['right']:
                    self.state = "wall"
                elif self.direction.y < 0:
                    self.state = "jump"
                else:
                    self.state = "fall"

    def damage(self):
        if not self.timers["hit"].active:
            self.data.health -= 1
            self.timers["hit"].activate()
            
    def flicker(self):
        if self.timers["hit"].active and sin(pygame.time.get_ticks()*100) >= 0:
            white_mask = pygame.mask.from_surface(self.image)
            white_surface = white_mask.to_surface()
            white_surface.set_colorkey((0, 0, 0))
            self.image = white_surface

    def update(self, dt):
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()
        self.input()
        self.platform_move(dt)
        self.move(dt)
        self.check_contact()
        self.get_state()
        self.animate(dt)
        self.flicker()