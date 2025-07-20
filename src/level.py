import pygame
from pygame import Vector2 as vector
from random import uniform
from math import sin

from config import *
from src.sprites import Sprite, MovingSprite, AnimatedSprite, Item, Spike, ParticleEffectSprite, Flag
from src.player import Player
from src.groups import AllSprites
from src.enemies import Tooth, Bombastic, Archer, Boss

class Level:
    def __init__(self, tmx_map, level_frames, audio_files, data, font, game=None):
        self.data = data
        self.font = font
        self.game = game

        self.level_width = tmx_map.width * 64
        self.level_bottom = tmx_map.height * 64
        tmx_level_properties = tmx_map.get_layer_by_name("Data")[0].properties
        if tmx_level_properties["bg"]:
            bg_tile = level_frames["bg_tiles"][tmx_level_properties["bg"]]
        else:
            bg_tile=None
        self.display = pygame.display.get_surface()
        self.tmx_map = tmx_map
        clouds_dict = {"large": level_frames["cloud_large"], "small": level_frames["cloud_small"]}
        self.all_sprites = AllSprites(tmx_map.width, tmx_map.height, clouds_dict, tmx_level_properties["horizon_line"], bg_tile)
        self.collision_sprites = pygame.sprite.Group()
        self.semi_collistion_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.tooth_sprites = pygame.sprite.Group()
        self.bombastic_sprites = pygame.sprite.Group()
        self.archer_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.flag_sprites = pygame.sprite.Group()
        self.boss_sprites = pygame.sprite.Group()

        self.near_flag = False
        self.boss_fight_started = False
        
        self.is_boss_level = "boss" in str(tmx_map)

        # Fog of war for boss fight
        self.fog_radius = 200  # Radius of visible area around player

        self.level_frames = level_frames
        self.setup(tmx_map, level_frames, audio_files)

        # audio
        self.coin_sound = audio_files['coin']
        self.coin_sound.set_volume(0.3)

    def setup(self, tmx_map, level_frames, audio_files):
        # tiles
        for layer in ["BG", "Terrain", "FG", "Platforms"]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == "Terrain": 
                    groups.append(self.collision_sprites)
                elif layer == "Platforms": groups.append(self.semi_collistion_sprites)
                match layer:
                    case "BG": z = ZLAYERS["bg tiles"]
                    case "FG": z = ZLAYERS["fg"]
                    case _: z = ZLAYERS["main"]

                Sprite((x*TILE_SIZE, y*TILE_SIZE), surf, groups, z)

        # bg details
        for obj in tmx_map.get_layer_by_name("BG details"):
            if obj.name == "static":
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, z = ZLAYERS["bg tiles"])
            else:
                AnimatedSprite((obj.x, obj.y), level_frames[obj.name], self.all_sprites, ZLAYERS["bg tiles"])
                if obj.name == "candle":
                    AnimatedSprite((obj.x, obj.y) + vector(-20, -20), level_frames["candle_light"], self.all_sprites, ZLAYERS["bg tiles"])

        # objects
        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "player":
                self.player = Player(
                    pos=(obj.x, obj.y),
                    groups=self.all_sprites,
                    collision_sprites= self.collision_sprites,
                    semi_collision_sprites= self.semi_collistion_sprites,
                    frames=level_frames["player"],
                    sounds = audio_files,
                    data = self.data
                )
            else:
                if obj.name in ("barrel", "crate"):
                    Sprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
                else:
                    frames = level_frames[obj.name] if not "palm" in obj.name else level_frames["palms"][obj.name]
                    if obj.name == "floor_spike" and obj.properties["inverted"]:
                        frames = [pygame.transform.flip(frame, False, True) for frame in frames]

                    groups = [self.all_sprites]
                    if obj.name in ("palm_small", "palm_large"): groups.append(self.semi_collistion_sprites)
                    if obj.name in ("saw", "floor_spike"): groups.append(self.damage_sprites)

                    z = ZLAYERS["main"] if not "bg" in obj.name else ZLAYERS["bg details"]

                    anim_speed = ANIMATION_SPEED if not "palm" in obj.name else 6 + uniform(-1, 1)
                    AnimatedSprite((obj.x, obj.y), frames, groups, z, anim_speed)
                    
                # Handle flag specially for boss fight interaction
                if obj.name == "flag":
                    flag_sprite = Flag(
                        pos=(obj.x + obj.width // 2, obj.y + obj.height // 2),
                        frames=level_frames["flag"],
                        groups=(self.all_sprites, self.flag_sprites),
                        z=ZLAYERS["main"]
                    )
                    self.boss_start_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

        # enemies
        for obj in tmx_map.get_layer_by_name("Enemies"):
            if obj.name == "tooth":
                Tooth((obj.x, obj.y), level_frames["tooth"], (self.all_sprites, self.damage_sprites, self.tooth_sprites), self.collision_sprites)
            elif obj.name == "bombastic":
                Bombastic((obj.x, obj.y), level_frames["bombastic"], level_frames["bombastic_explosion"], level_frames["bombastic_dead"], (self.all_sprites, self.damage_sprites, self.bombastic_sprites), self.player, audio_files)
            elif obj.name == "archer":
                Archer((obj.x, obj.y), level_frames["archer"], (self.all_sprites, self.damage_sprites, self.archer_sprites), self.collision_sprites, self.player, audio_files)
        
        if self.is_boss_level:
            # Spawn boss in the center of the level
            boss_x = (tmx_map.width * TILE_SIZE) // 2
            boss_y = (tmx_map.height * TILE_SIZE) // 2 - 100
            Boss((boss_x, boss_y), (self.all_sprites, self.damage_sprites, self.boss_sprites), self.player)

        # moving objects
        for obj in tmx_map.get_layer_by_name("Moving Objects"):
            if obj.name == "spike":
                Spike(
                    pos = (obj.x + obj.width / 2, obj.y + obj.height / 2),
                    surf = level_frames["spike"],
                    radius = obj.properties["radius"],
                    speed = obj.properties["speed"],
                    start_angle = obj.properties["start_angle"],
                    end_angle = obj.properties["end_angle"],
                    groups = (self.all_sprites, self.damage_sprites),
                )
                for i in range(0, obj.properties["radius"], 20):
                    Spike(
                        pos = (obj.x + obj.width / 2, obj.y + obj.height / 2),
                        surf = level_frames["spike_chain"],
                        radius = i,
                        speed = obj.properties["speed"],
                        start_angle = obj.properties["start_angle"],
                        end_angle = obj.properties["end_angle"],
                        groups = self.all_sprites,
                        z = ZLAYERS["bg details"],
                    )
            else:
                frames = level_frames[obj.name]
                groups = (self.all_sprites, self.semi_collistion_sprites) if obj.properties["platform"] else (self.all_sprites, self.damage_sprites)
                if obj.width > obj.height:
                    move_dir = 'x'
                    start_pos = (obj.x, obj.y + obj.height // 2)
                    end_pos = (obj.x + obj.width, obj.y + obj.height // 2)
                else:
                    move_dir = 'y'
                    start_pos = (obj.x + obj.width // 2, obj.y)
                    end_pos = (obj.x + obj.width // 2, obj.y + obj.height)
                speed = obj.properties["speed"]
                MovingSprite(frames, groups, start_pos, end_pos, speed, move_dir, obj.properties["flip"])

                if obj.name == "saw":
                    if move_dir == 'x':
                        y = start_pos[1] - level_frames["saw_chain"].get_height() // 2
                        left, right = int(start_pos[0]), int(end_pos[0])
                        for x in range(left, right, 20):
                            Sprite((x, y), level_frames["saw_chain"], self.all_sprites, ZLAYERS["bg details"])
                    else:
                        x = start_pos[0] - level_frames["saw_chain"].get_width() // 2
                        top, bottom = int(start_pos[1]), int(end_pos[1])
                        for y in range(top, bottom, 20):
                            Sprite((x, y), level_frames["saw_chain"], self.all_sprites, ZLAYERS["bg details"])

        # items
        for obj in tmx_map.get_layer_by_name("Items"):
            Item(obj.name, (obj.x + 32, obj.y + 32), level_frames["items"][obj.name], (self.all_sprites, self.item_sprites), self.data)

        # water
        for obj in tmx_map.get_layer_by_name("Water"):
                rows = int(obj.height / 64)
                cols = int(obj.width / 64)
                for row in range(rows):
                    for col in range(cols):
                        x = obj.x + col * 64
                        y = obj.y + row * 64
                        if row == 0:
                            AnimatedSprite((x, y), level_frames["water_top"], self.all_sprites, ZLAYERS["water"])
                        else:
                            Sprite((x, y), level_frames["water_body"], self.all_sprites, ZLAYERS["water"])
    
    def item_collision(self):
        if self.item_sprites:
            item_sprites = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            if item_sprites:
                item_sprites[0].activate()
                ParticleEffectSprite((item_sprites[0].rect.center), self.level_frames["particle"], self.all_sprites)
                self.coin_sound.play()

    def hit_collision(self):
        for sprite in self.damage_sprites.sprites():
            if sprite.rect.colliderect(self.player.hitbox_rect):
                self.player.damage()

    def attack_collision(self):
        for target in self.tooth_sprites.sprites():
            facing_target = (self.player.rect.centerx < target.rect.centerx and self.player.face_right) or \
                            (self.player.rect.centerx > target.rect.centerx and not self.player.face_right)

            if target.rect.colliderect(self.player.rect) and self.player.attacking and facing_target:
                target.reverse()
        

        for target in self.bombastic_sprites.sprites():
            facing_target = (self.player.rect.centerx < target.rect.centerx and self.player.face_right) or \
                            (self.player.rect.centerx > target.rect.centerx and not self.player.face_right)

            if target.hitbox_rect.colliderect(self.player.rect) and self.player.attacking and facing_target and target.state == "chasing":
                target.take_damage()

        # Boss attack collision
        for target in self.boss_sprites.sprites():
            facing_target = (self.player.rect.centerx < target.rect.centerx and self.player.face_right) or \
                            (self.player.rect.centerx > target.rect.centerx and not self.player.face_right)

            if target.hitbox_rect.colliderect(self.player.rect) and self.player.attacking and facing_target:
                target.take_damage()

    def check_constraint(self):
        # left & right borders
        if self.player.hitbox_rect.left <= 0:
            self.player.hitbox_rect.left = 0
        elif self.player.hitbox_rect.right >= self.level_width:
            self.player.hitbox_rect.right = self.level_width

        # bottom border
        if self.player.hitbox_rect.bottom >= self.level_bottom:
            print("death")
                
    def flag_interaction(self):
        if self.flag_sprites and not self.boss_fight_started:
            flag = self.flag_sprites.sprites()[0]  # Assuming one flag per level
            
            # Check if player is close enough to interact
            self.near_flag = flag.can_interact(self.player.hitbox_rect)
            
            # Visual feedback could be added here (like showing "Press E to interact")
            
    def start_boss_fight(self):
        if not self.boss_fight_started and self.game:
            self.boss_fight_started = True
            print("Switching to boss level...")
            self.game.switch_to_boss_level()
            return True
        return False

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if self.near_flag and not self.boss_fight_started:
                        # Player clicked while near flag
                        if self.flag_sprites:
                            flag = self.flag_sprites.sprites()[0]
                            if flag.interact():
                                self.start_boss_fight()

    def draw_ui_elements(self):
        if self.near_flag and not self.boss_fight_started:
            pulse = abs(sin(pygame.time.get_ticks() * 0.005)) * 0.3 + 0.7  # Pulse between 0.7 and 1.0
            
            gold_color = (int(255 * pulse), int(215 * pulse), 0)
            shadow_color = (int(139 * pulse), int(69 * pulse), int(19 * pulse))
            
            text = self.font.render("Click to start Boss Fight!", True, gold_color)
            text_rect = text.get_rect(center=(self.display.get_width() // 2, 50))
            
            shadow_text = self.font.render("Click to start Boss Fight!", True, shadow_color)
            shadow_rect = shadow_text.get_rect(center=(self.display.get_width() // 2 + 2, 52))
            
            self.display.blit(shadow_text, shadow_rect)
            self.display.blit(text, text_rect)


    def draw_boss_health(self):
        if self.boss_sprites:
            boss = self.boss_sprites.sprites()[0]
            # Draw health bar at the top of the screen
            bar_width = 400
            bar_height = 20
            bar_x = (self.display.get_width() - bar_width) // 2
            bar_y = 20
            
            # Background bar
            pygame.draw.rect(self.display, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            
            # Health bar
            health_percentage = boss.health / boss.max_health
            health_width = int(bar_width * health_percentage)
            pygame.draw.rect(self.display, (200, 0, 0), (bar_x, bar_y, health_width, bar_height))
            
            # Border
            pygame.draw.rect(self.display, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Boss name
            boss_text = self.font.render("BOSS", True, (255, 255, 255))
            boss_rect = boss_text.get_rect(center=(self.display.get_width() // 2, bar_y - 15))
            self.display.blit(boss_text, boss_rect)

    def draw_fog_of_war(self):
        if self.is_boss_level:
            # Create a surface for the fog effect
            fog_surface = pygame.Surface((self.display.get_width(), self.display.get_height()), pygame.SRCALPHA)
            
            # Get player's screen position
            camera_offset = self.all_sprites.offset
            player_screen_pos = (
                int(self.player.hitbox_rect.centerx + camera_offset.x),
                int(self.player.hitbox_rect.centery + camera_offset.y)
            )
            
            # Fill the entire screen with a dark color
            fog_surface.fill((0, 0, 0, 220))

            # Create a gradient effect for a soft edge
            for i in range(60):
                radius = self.fog_radius - i * 3
                alpha = 220 - i * 3.5
                if radius > 0 and alpha > 0:
                    pygame.draw.circle(fog_surface, (0,0,0,alpha), player_screen_pos, radius)

            # Blit the fog surface onto the display
            self.display.blit(fog_surface, (0, 0))

    def run(self, dt):
        self.all_sprites.update(dt)
        self.item_collision()
        self.hit_collision()
        self.attack_collision()
        self.check_constraint()
        self.flag_interaction()

        self.all_sprites.draw(self.player.hitbox_rect.center, dt)
        self.draw_ui_elements()
        self.draw_boss_health()
        self.draw_fog_of_war()