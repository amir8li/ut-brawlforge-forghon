import pygame
from pygame.math import Vector2 as vector
from math import sin
from config import *
from src.timer import Timer
from src.sprites import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, semi_collision_sprites, frames, sounds, data, player_id=0, game=None):
        super().__init__(groups)
        self.game = game
        self.is_local = False 
        self.username = "Player"
        self.network_pos = vector(pos)

        self.is_player = True
        self.shield_active = False
        self.buff_damage_enabled = False
        self.double_jump_enabled = False
        self.has_double_jumped = False
        self.all_sprites = groups
        self.frames = frames
        self.frame_index = 0
        self.state = "idle"
        self.face_right = True
        self.data = data
        self.sounds = sounds
        self.player_id = player_id
        self.bullets = []

        if self.data.name == "player2":
            for key in self.frames:
                self.frames[key] = [pygame.transform.smoothscale(img, (img.get_width()*2, img.get_height()*2)) for img in self.frames[key]]
        
        self.image = self.frames[self.state][self.frame_index]
        self.z = ZLAYERS["main"]
        adjusted_pos = list(pos)

        if self.data.name == "player3":
            adjusted_pos[1] += 30
            
        self.rect = self.image.get_rect(topleft=adjusted_pos)
        self.hitbox_rect = self.rect.inflate(-76, -36)
        self.old_rect = self.hitbox_rect.copy()
        self.direction = vector(0, 0)
        self.speed = PLAYER_SPEED
        self.gravity = GRAVITY
        self.jump = False
        self.can_jump = True
        self.jump_height = JUMP_HEIGHT
        self.attacking = False
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.on_surface = {'left': False, 'right': False, 'top': False, 'floor': False}
        self.platform = None
        self.timers = { "wall_jump": Timer(500), "wall_slide": Timer(250), "platform_skip": Timer(100), "attack_cooldown": Timer(500), "hit": Timer(800), "shoot_cooldown": Timer(BULLET_COOLDOWN * 1000),}
        self.attack_sound = sounds['attack']
        self.attack_sound.set_volume(0.3)
        self.jump_sound = sounds['jump']
        self.jump_sound.set_volume(0.3)
        self.bullet_sound = sounds['bullet']
        self.bullet_sound.set_volume(0.3)
        self.damaged_sound = sounds['damage']
        self.damaged_sound.set_volume(0.6)
        self.frozen = False
        self.frozen_timer = Timer(0)

    def freeze(self, duration):
        self.frozen = True
        self.frozen_timer = Timer(duration)
        self.frozen_timer.activate()

    def update_from_network(self, data):
        if not self.is_local:
            self.network_pos.x, self.network_pos.y = data['pos']
            self.state = data['state']
            self.face_right = data['face_right']
            self.data.health = data['health']

    def input(self):
        if not self.is_local:
            return

        if self.frozen:
            self.direction.x = 0
            self.jump = False
            return
        
        keys = pygame.key.get_pressed()
        input_vector = vector(0, 0)

        if not self.timers["wall_jump"].active:
            if self.player_id == 0:
                if keys[pygame.K_d]:
                    input_vector.x += 1
                    self.face_right = True
                if keys[pygame.K_a]:
                    input_vector.x -= 1
                    self.face_right = False
                if keys[pygame.K_s]:
                    self.timers["platform_skip"].activate()
                if pygame.mouse.get_pressed()[0]:
                    self.attack()
                if pygame.mouse.get_pressed()[2]:
                    self.shoot()
                if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.can_jump:
                    self.jump = True
                    self.can_jump = False
                elif not (keys[pygame.K_SPACE] or keys[pygame.K_w]):
                    self.can_jump = True

            else:
                if keys[pygame.K_RIGHT]:
                    input_vector.x += 1
                    self.face_right = True
                if keys[pygame.K_LEFT]:
                    input_vector.x -= 1
                    self.face_right = False
                if keys[pygame.K_DOWN]:
                    self.timers["platform_skip"].activate()
                if keys[pygame.K_KP1]:
                    self.attack()
                if keys[pygame.K_KP2]:
                    self.shoot()
                if keys[pygame.K_UP] and self.can_jump:
                    self.jump = True
                    self.can_jump = False
                elif not keys[pygame.K_UP]:
                    self.can_jump = True

            if not self.timers["hit"].active:
                if input_vector:
                    self.direction.x = input_vector.normalize().x
                else:
                    self.direction.x = 0

    def attack(self):
        if not self.timers["attack_cooldown"].active:
            self.attacking = True
            self.frame_index = 0
            self.timers["attack_cooldown"].activate()
            self.attack_sound.play()
            self.attacked_enemies = []

    def shoot(self):
        if not self.timers["shoot_cooldown"].active:
            spawn_pos = (self.rect.centerx, self.rect.centery)
            bullet = Bullet(
                pos=spawn_pos,
                surf=self.frames["bullet"][0],
                direction=vector(1, 0) if self.face_right else vector(-1, 0),
                speed=BULLET_SPEED,
                groups=[self.all_sprites]
            )
            self.bullets.append(bullet)
            self.bullet_sound.play()
            self.timers["shoot_cooldown"].activate()

    def move(self, dt):
        if self.frozen:
            return
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
                self.hitbox_rect.bottom -= 1
                self.timers["wall_slide"].activate()
                self.jump_sound.play()
                self.has_double_jumped = False
            elif any((self.on_surface['left'], self.on_surface['right'])) and not self.timers["wall_slide"].active:
                self.timers["wall_jump"].activate()
                self.direction.y = self.jump_height
                self.direction.x = 0.5 if self.on_surface['left'] else -0.5
                self.hitbox_rect.x += 4 if self.on_surface['left'] else -4
                self.hitbox_rect.y -= 6
                self.jump_sound.play()
                self.has_double_jumped = False
            elif self.double_jump_enabled and not self.has_double_jumped and not self.on_surface['floor']:
                self.direction.y = self.jump_height
                self.jump_sound.play()
                self.has_double_jumped = True
            self.jump = False

        self.collision('vertical')
        self.semi_collision()
        self.rect.center = self.hitbox_rect.center

    def platform_move(self, dt):
        if self.platform and not self.timers["wall_jump"].active:
            self.hitbox_rect.topleft += self.platform.direction * self.platform.speed * dt

    def check_contact(self):
        floor_rect = pygame.Rect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 2))
        right_rect = pygame.Rect(self.hitbox_rect.topright + vector(0, self.hitbox_rect.height / 4), (2, self.hitbox_rect.height / 2))
        left_rect = pygame.Rect(self.hitbox_rect.topleft + vector(-2, self.hitbox_rect.height / 4), (2, self.hitbox_rect.height / 2))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        semi_collide_rects = [sprite.rect for sprite in self.semi_collision_sprites]

        self.on_surface['floor'] = floor_rect.collidelist(collide_rects) >= 0 or \
            (floor_rect.collidelist(semi_collide_rects) >= 0 and self.direction.y >= 0)
        self.on_surface['right'] = right_rect.collidelist(collide_rects) >= 0
        self.on_surface['left'] = left_rect.collidelist(collide_rects) >= 0

        self.platform = None
        sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
        for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
            if sprite.rect.colliderect(floor_rect) and self.direction.y >= 0 and not self.timers["wall_jump"].active:
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
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                    self.direction.y = 0

    def semi_collision(self):
        if not self.timers["platform_skip"].active and not self.timers["wall_jump"].active:
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

    def knockback_from(self, attacker):
        if not self.timers["hit"].active:
            self.timers["hit"].activate()
            self.damaged_sound.play()

            
        offset = 10
        direction = 1 if attacker.rect.centerx < self.rect.centerx else -1
        self.hitbox_rect.x += direction * offset
        self.rect.center = self.hitbox_rect.center

    def damage(self, knockback=True):
        if not self.is_local:
            return

        if self.shield_active:
            return
        if not self.timers["hit"].active:
            dmg = 1
            if self.buff_damage_enabled:
                dmg = 2
            self.data.health -= dmg
            self.timers["hit"].activate()
            if not knockback:
                return
                
            
    def flicker(self):
        if self.timers["hit"].active and sin(pygame.time.get_ticks()*100) >= 0:
            white_mask = pygame.mask.from_surface(self.image)
            white_surface = white_mask.to_surface()
            white_surface.set_colorkey((0, 0, 0))
            self.image = white_surface

    def enable_double_jump(self):
        self.double_jump_enabled = True
        self.double_jump_timer = pygame.time.get_ticks()
        self.double_jump_duration = 10000
        self.has_double_jumped = False

    def buff_damage(self):
        self.buff_damage_enabled = True
        self.buff_timer = pygame.time.get_ticks()
        self.buff_duration = 8000

    def activate_shield(self):
        self.shield_active = True
        self.shield_timer = pygame.time.get_ticks()
        self.shield_duration = 12000

    def draw_shield(self, surface):
        if self.shield_active:
            shield_color = (0, 255, 255, 100)
            shield_radius = max(self.rect.width, self.rect.height) // 2 + 10
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, shield_color, (shield_radius, shield_radius), shield_radius)
            shield_rect = shield_surface.get_rect(center=self.hitbox_rect.center)
            surface.blit(shield_surface, shield_rect)

    def update(self, dt):
        if self.frozen:
            self.frozen_timer.update()
            if not self.frozen_timer.active:
                self.frozen = False

        if self.is_local:
            self.old_rect = self.hitbox_rect.copy()
            self.update_timers()
            self.input()
            self.platform_move(dt)
            self.move(dt)
            self.check_contact()

        else:
            interpolation_factor = 0.2 
            current_pos = vector(self.hitbox_rect.topleft)
            self.hitbox_rect.topleft = current_pos.lerp(self.network_pos, interpolation_factor)
            self.rect.center = self.hitbox_rect.center

        self.get_state()
        self.animate(dt)
        self.flicker()
        if self.frozen:
            self.state = "idle"

        current_time = pygame.time.get_ticks()
        if self.double_jump_enabled and hasattr(self, 'double_jump_timer') and current_time - self.double_jump_timer > self.double_jump_duration:
            self.double_jump_enabled = False
            self.has_double_jumped = False
        if self.buff_damage_enabled and hasattr(self, 'buff_timer') and current_time - self.buff_timer > self.buff_duration:
            self.buff_damage_enabled = False
        if self.shield_active and hasattr(self, 'shield_timer') and current_time - self.shield_timer > self.shield_duration:
            self.shield_active = False
