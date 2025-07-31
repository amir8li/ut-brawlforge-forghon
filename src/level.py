import pygame
import os
from pygame import Vector2 as vector
from random import uniform
from math import sin
from itertools import chain

from config import *
from src.sprites import Sprite, MovingSprite, AnimatedSprite, Item, Spike, ParticleEffectSprite, Flag
from src.player import Player
from src.groups import AllSprites
from src.enemies import Tooth, Bombastic, Archer, IceWizard, Boss
from src.powerup import PowerUp

class Level:
    def __init__(self, tmx_map, level_frames, audio_files, data, font, game=None, powerup_locations=None, current_level=1):
        self.data = data
        self.font = font
        self.game = game
        self.current_level = current_level
        self.is_boss_level = "boss" in str(tmx_map.filename).lower() if hasattr(tmx_map, 'filename') and tmx_map.filename else False
        self.level_width = tmx_map.width * 64
        self.level_bottom = tmx_map.height * 64
        tmx_level_properties = tmx_map.get_layer_by_name("Data")[0].properties
        if tmx_level_properties["bg"]:
            bg_tile = level_frames["bg_tiles"][tmx_level_properties["bg"]]
        else:
            bg_tile=None
        self.display = pygame.display.get_surface()
        self.tmx_map = tmx_map
        self.display = pygame.display.get_surface()
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_bottom = tmx_map.height * TILE_SIZE
        self.multiplayer = len(data) > 1
        self.powerup_locations = powerup_locations or {}
        self.audio_files = audio_files

        tmx_level_properties = tmx_map.get_layer_by_name("Data")[0].properties
        bg_tile = level_frames["bg_tiles"][tmx_level_properties["bg"]] if tmx_level_properties["bg"] else None
        clouds_dict = {"large": level_frames["cloud_large"], "small": level_frames["cloud_small"]}

        self.all_sprites = AllSprites(
            tmx_map.width, tmx_map.height,
            clouds_dict, tmx_level_properties["horizon_line"], bg_tile
        )
        self.enemy_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()
        self.platform_sprites_for_enemies = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.tooth_sprites = pygame.sprite.Group()
        self.bombastic_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.ice_wizard_sprites = pygame.sprite.Group()
        self.archer_sprites = pygame.sprite.Group()
        self.flag_sprites = pygame.sprite.Group()
        self.boss_sprites = pygame.sprite.Group()

        self.near_flag = False
        self.boss_fight_started = False
        
        self.is_boss_level = "boss" in str(tmx_map)

        # Fog of war for boss fight
        self.fog_radius = 200  # Radius of visible area around player

        self.initial_item_count = 0
        self.powerup_sprites = pygame.sprite.Group()
        self.level_frames = level_frames
        self.coin_sound = audio_files['coin']
        self.coin_sound.set_volume(0.3)
        self.players = []

        self.setup(tmx_map, level_frames, audio_files)

    def setup(self, tmx_map, level_frames, audio_files):
        for layer in ["BG", "Terrain", "FG", "Platforms"]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == "Terrain": groups.append(self.collision_sprites)
                elif layer == "Platforms":
                    groups.append(self.semi_collision_sprites)
                    groups.append(self.platform_sprites_for_enemies)
                match layer:
                    case "BG": z = ZLAYERS["bg tiles"]
                    case "FG": z = ZLAYERS["fg"]
                    case _: z = ZLAYERS["main"]
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, z)

        for obj in tmx_map.get_layer_by_name("BG details"):
            if obj.name == "static":
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, z=ZLAYERS["bg tiles"])
            else:
                AnimatedSprite((obj.x, obj.y), level_frames[obj.name], self.all_sprites, ZLAYERS["bg tiles"])
                if obj.name == "candle":
                    AnimatedSprite((obj.x, obj.y) + vector(-20, -20), level_frames["candle_light"], self.all_sprites, ZLAYERS["bg tiles"])

        player_positions = []
        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "player":
                player_positions.append((obj.x, obj.y))
            elif obj.name in ("barrel", "crate"):
                Sprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
            else:
                frames = level_frames[obj.name] if "palm" not in obj.name else level_frames["palms"][obj.name]
                if obj.name == "floor_spike" and obj.properties.get("inverted", False):
                    frames = [pygame.transform.flip(frame, False, True) for frame in frames]
                groups = [self.all_sprites]
                if obj.name in ("palm_small", "palm_large"):
                    groups.append(self.semi_collision_sprites)
                if obj.name in ("saw", "floor_spike"):
                    groups.append(self.damage_sprites)
                z = ZLAYERS["main"] if "bg" not in obj.name else ZLAYERS["bg details"]
                anim_speed = ANIMATION_SPEED if "palm" not in obj.name else 6 + uniform(-1, 1)
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

        if not player_positions:
            player_positions = [(100, 200), (300, 200)]

        for i, data in enumerate(self.data):
            base_pos = player_positions[i % len(player_positions)]
            spawn_offset = 100 * i
            player_pos = (base_pos[0] + spawn_offset, base_pos[1])
            player = Player(
                pos=player_pos,
                groups=self.all_sprites,
                collision_sprites=self.collision_sprites,
                semi_collision_sprites=self.semi_collision_sprites,
                frames=level_frames["player"][i] if isinstance(level_frames["player"], list) else level_frames["player"],
                sounds=self.audio_files,
                data=data,
                player_id=i
            )
            self.players.append(player)


        # enemies
        all_collision_sprites = pygame.sprite.Group(chain(self.collision_sprites.sprites(), self.platform_sprites_for_enemies.sprites()))
        for obj in tmx_map.get_layer_by_name("Enemies"):
            player_to_follow = self.players[0]
            if obj.name == "tooth":
                Tooth(pos=(obj.x, obj.y), frames=level_frames["tooth"], groups=(self.all_sprites, self.damage_sprites, self.tooth_sprites, self.enemy_sprites), collision_sprites=all_collision_sprites, player=player_to_follow, sounds=audio_files)
            elif obj.name == "bombastic":
                Bombastic(pos=(obj.x, obj.y), frames=level_frames["bombastic"], explosion_frames=level_frames["bombastic_explosion"], dead_frames=level_frames["bombastic_dead"], groups=(self.all_sprites, self.damage_sprites, self.bombastic_sprites, self.enemy_sprites), player=player_to_follow, sounds=audio_files)
            elif obj.name == "archer":
                Archer(pos=(obj.x, obj.y), frames=level_frames["archer"], groups=(self.all_sprites, self.damage_sprites, self.archer_sprites, self.enemy_sprites), collision_sprites=all_collision_sprites, player=player_to_follow, sounds=audio_files)
            elif obj.name == "ice wizard":
                IceWizard(pos=(obj.x, obj.y), frames=level_frames["ice_wizard"], groups=(self.all_sprites, self.damage_sprites, self.ice_wizard_sprites, self.enemy_sprites), player=player_to_follow, sounds=audio_files)
        if self.is_boss_level:
            if os.path.basename(tmx_map.filename) == "boss 5.tmx":
                boss_x = (tmx_map.width * TILE_SIZE) // 2
                boss_y = (tmx_map.height * TILE_SIZE) // 2 - 100
                Boss((boss_x, boss_y), (self.all_sprites, self.damage_sprites, self.boss_sprites), self.players[0])

        self.initial_enemy_count = len(self.enemy_sprites)

        if self.multiplayer and tmx_map.get_layer_by_name("powerups"):
            for obj in tmx_map.get_layer_by_name("powerups"):
                power_type = obj.name
                if power_type in level_frames["powerups"]:
                    surf = level_frames["powerups"][power_type]
                    PowerUp(
                        pos=(obj.x + obj.width / 2, obj.y + obj.height / 2),
                        power_type=power_type,
                        surf=surf,
                        groups=[self.all_sprites, self.powerup_sprites]
                    )

        # moving objects
        for obj in tmx_map.get_layer_by_name("Moving Objects"):
            if obj.name == "spike":
                surf = level_frames["spike"]
                if isinstance(surf, list):
                    surf = surf[0]
                Spike(
                    pos=(obj.x + obj.width / 2, obj.y + obj.height / 2),
                    surf=surf,
                    radius=obj.properties.get("radius", 100),
                    speed=obj.properties.get("speed", 50),
                    start_angle=obj.properties.get("start_angle", 0),
                    end_angle=obj.properties.get("end_angle", -1),
                    groups=(self.all_sprites, self.damage_sprites),
                )
                for i in range(0, obj.properties.get("radius", 100), 20):
                    Spike(
                        pos=(obj.x + obj.width / 2, obj.y + obj.height / 2),
                        surf=level_frames["spike_chain"],
                        radius=i,
                        speed=obj.properties.get("speed", 50),
                        start_angle=obj.properties.get("start_angle", 0),
                        end_angle=obj.properties.get("end_angle", -1),
                        groups=self.all_sprites,
                        z=ZLAYERS["bg details"],
                    )
            else:
                frames = level_frames[obj.name]
                if isinstance(frames, pygame.Surface):
                    frames = [frames]
                is_platform = obj.properties.get("platform", False)
                is_harmful = obj.properties.get("harmful", False)
                groups = [self.all_sprites]
                if is_platform:
                    groups.append(self.semi_collision_sprites)
                elif is_harmful:
                    groups.append(self.damage_sprites)
                else:
                    groups.append(self.collision_sprites)

                if obj.width > obj.height:
                    move_dir = 'x'
                    start_pos = (obj.x, obj.y + obj.height // 2)
                    end_pos = (obj.x + obj.width, obj.y + obj.height // 2)
                else:
                    move_dir = 'y'
                    start_pos = (obj.x + obj.width // 2, obj.y)
                    end_pos = (obj.x + obj.width // 2, obj.y + obj.height)

                speed = obj.properties.get("speed", 1)
                flip = obj.properties.get("flip", False)
                MovingSprite(frames, tuple(groups), start_pos, end_pos, speed, move_dir, flip)

                if obj.name == "saw":
                    chain_surf = level_frames["saw_chain"]
                    if move_dir == "x":
                        y = start_pos[1] - chain_surf.get_height() // 2
                        for x in range(int(start_pos[0]), int(end_pos[0]), 20):
                            Sprite((x, y), chain_surf, self.all_sprites, ZLAYERS["bg details"])
                    else:
                        x = start_pos[0] - chain_surf.get_width() // 2
                        for y in range(int(start_pos[1]), int(end_pos[1]), 20):
                            Sprite((x, y), chain_surf, self.all_sprites, ZLAYERS["bg details"])

        # if len(self.data) == 1: 
        #     for obj in tmx_map.get_layer_by_name("Enemies"):
        #         if obj.name == "tooth":
        #             Tooth((obj.x, obj.y), level_frames["tooth"], (self.all_sprites, self.damage_sprites, self.tooth_sprites), self.collision_sprites, audio_files, self.players[0])

            for obj in tmx_map.get_layer_by_name("Items"):
                Item(obj.name, (obj.x + 32, obj.y + 32), level_frames["items"][obj.name], (self.all_sprites, self.item_sprites), self.data)

            self.initial_item_count = len(self.item_sprites)

        for obj in tmx_map.get_layer_by_name("Water"):
            rows = int(obj.height / 64)
            cols = int(obj.width / 64)
            for row in range(rows):
                for col in range(cols):
                    x = obj.x + col * 64
                    y = obj.y + row * 64
                    if row == 0:
                        AnimatedSprite((x, y), self.level_frames["water_top"], self.all_sprites, ZLAYERS["water"])
                    else:
                        Sprite((x, y), self.level_frames["water_body"], self.all_sprites, ZLAYERS["water"])

    def powerup_collision(self):
        for player in self.players:
            collided_powerups = pygame.sprite.spritecollide(player, self.powerup_sprites, True)
            for powerup in collided_powerups:
                if powerup.power_type == "double_jump":
                    player.enable_double_jump()
                elif powerup.power_type == "magic":
                    player.buff_damage()  
                elif powerup.power_type == "shield":
                    player.activate_shield()
                
                if 'particle' in self.level_frames:
                    ParticleEffectSprite(powerup.rect.center, self.level_frames['particle'], self.all_sprites)
                if 'coin' in self.audio_files:
                    self.audio_files['coin'].play()

    def item_collision(self):
        for player in self.players:
            item_sprites = pygame.sprite.spritecollide(player, self.item_sprites, True)
            for item in item_sprites:
                item.activate(player.data)
                ParticleEffectSprite(item.rect.center, self.level_frames["particle"], self.all_sprites)
                self.coin_sound.play()

    def hit_collision(self):
        for sprite in self.damage_sprites.sprites():
            if sprite.rect.colliderect(self.players[0].hitbox_rect):
                self.players[0].damage()
        for sprite in self.all_sprites:
            if hasattr(sprite, 'player') and hasattr(sprite, 'direction') and hasattr(sprite, 'facing_right'):
                if sprite.rect.colliderect(self.players[0].rect):
                    player_x = self.players[0].rect.centerx
                    archer_x = sprite.rect.centerx
                    if (sprite.direction > 0 and player_x < archer_x) or (sprite.direction < 0 and player_x > archer_x):
                        sprite.direction *= -1
                        sprite.facing_right = sprite.direction > 0

    def attack_collision(self):
        enemy_sprites = self.tooth_sprites.sprites() + self.bombastic_sprites.sprites() + self.archer_sprites.sprites() + self.ice_wizard_sprites.sprites()
        
        for target in enemy_sprites:
            facing_target = (self.players[0].rect.centerx < target.rect.centerx and self.players[0].face_right) or \
                            (self.players[0].rect.centerx > target.rect.centerx and not self.players[0].face_right)

            if target.hitbox_rect.colliderect(self.players[0].rect) and self.players[0].attacking and facing_target:
                if target not in self.players[0].attacked_enemies:
                    target.take_damage()
                    self.players[0].attacked_enemies.append(target)

        # Boss attack collision
        for target in self.boss_sprites.sprites():
            facing_target = (self.players[0].rect.centerx < target.rect.centerx and self.players[0].face_right) or \
                            (self.players[0].rect.centerx > target.rect.centerx and not self.players[0].face_right)

            if target.hitbox_rect.colliderect(self.players[0].rect) and self.players[0].attacking and facing_target:
                target.take_damage()
    
        for player in self.players:
            for sprite in self.damage_sprites:
                offset = (sprite.rect.left - player.rect.left, sprite.rect.top - player.rect.top)
                if pygame.sprite.collide_mask(player, sprite):
                    player.damage(knockback=False)

        affected_targets = set()
        for i, attacker in enumerate(self.players):
            for j, target in enumerate(self.players):
                if i == j or target in affected_targets:
                    continue
                if attacker.attacking:
                    facing_target = (
                        attacker.rect.centerx < target.rect.centerx and attacker.face_right
                    ) or (
                        attacker.rect.centerx > target.rect.centerx and not attacker.face_right
                    )
                    if target.rect.colliderect(attacker.rect) and facing_target:
                        target.knockback_from(attacker)
                        affected_targets.add(target)

        if not self.multiplayer:
            for player in self.players:
                for target in self.tooth_sprites:
                    facing_target = (
                        player.rect.centerx < target.rect.centerx and player.face_right
                    ) or (
                        player.rect.centerx > target.rect.centerx and not player.face_right
                    )
                    if target.rect.colliderect(player.rect) and player.attacking and facing_target:
                        if hasattr(target, 'reverse') and callable(getattr(target, 'reverse')):
                            target.reverse()

    def bullet_collision(self):
        for i, attacker in enumerate(self.players):
            for bullet in attacker.bullets:
                for j, target in enumerate(self.players):
                    if i != j and bullet.rect.colliderect(target.rect):
                        if not target.timers["hit"].active:
                            target.damage()
                            bullet.kill()
                            if bullet in attacker.bullets:
                                attacker.bullets.remove(bullet)

    def check_constraint(self):
       
        alive = [p for p in self.players if p.data.health > 0 and p.hitbox_rect.bottom < self.level_bottom + 300]
        if len(alive) == 0:
            return "gameover"
        if len(alive) == 1 and self.multiplayer:
            return f"{alive[0].data.name} won"
   
        if self.is_boss_level:
            if len(self.tooth_sprites) == 0 and len(self.boss_sprites) == 0:
                return "win" 
        
        return None
        
    def spawn_powerups(self):
        map_name = os.path.basename(self.tmx_map.filename)
        powerup_types = self.level_frames["powerups"]
        durations = {
            "double_jump": 10000,
            "magic": 8000,
            "shield": 12000
        }

        positions = self.powerup_locations.get(map_name, {})

        for power_type, image in powerup_types.items():
            coords = positions.get(power_type, [])
            for pos in coords:
                powerup = PowerUp(power_type, pos, image, duration=durations.get(power_type, 8000))
                self.powerup_sprites.add(powerup)
                self.all_sprites.add(powerup)
                
    def flag_interaction(self):
        if self.flag_sprites and not self.boss_fight_started:
            flag = self.flag_sprites.sprites()[0]  # Assuming one flag per level
            # Use the first player for single player mode
            player = self.players[0]
            # Check if player is close enough to interact
            self.near_flag = flag.can_interact(player.hitbox_rect)

        
    def start_boss_fight(self):
        if not self.boss_fight_started and self.game:
            self.boss_fight_started = True
            print("Signal to start boss sequence sent...")
           
            self.game.request_boss_sequence() 
            return True
        return False

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.near_flag and not self.boss_fight_started:
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
                int(self.players[0].hitbox_rect.centerx + camera_offset.x),
                int(self.players[0].hitbox_rect.centery + camera_offset.y)
            )

            # Make the fog less opaque for better readability
            base_alpha = 120  # was 220
            fog_surface.fill((0, 0, 0, base_alpha))

            # Create a gradient effect for a soft edge, also less opaque
            for i in range(60):
                radius = self.fog_radius - i * 3
                alpha = base_alpha - i * 2  # softer gradient
                if radius > 0 and alpha > 0:
                    pygame.draw.circle(fog_surface, (0, 0, 0, alpha), player_screen_pos, radius)

            # Blit the fog surface onto the display
            self.display.blit(fog_surface, (0, 0))


    def update(self, dt):
        self.all_sprites.update(dt)
        self.powerup_sprites.update(dt)
        self.item_collision()
        self.hit_collision()
        self.attack_collision()
        self.bullet_collision()
        self.powerup_collision()
        self.check_constraint()
        self.flag_interaction()
        if self.multiplayer:
            self.powerup_collision()

        self.all_sprites.draw(self.players[0].hitbox_rect.center, dt)

    def draw(self, surface):
        self.all_sprites.custom_draw(self.players[0] if len(self.players) == 1 else self.players)

        for boss in self.boss_sprites:
            if hasattr(boss, 'draw_talk'):
                boss.draw_talk(surface, self.font)
        self.draw_ui_elements()
        self.draw_boss_health()
        self.draw_fog_of_war()
        for player in self.players:
            player.draw_shield(surface)


