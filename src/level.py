import pygame
from src.sprites import Sprite, MovingSprite, AnimatedSprite, Item, Spike
from src.player import Player
from src.groups import AllSprites
from random import uniform

class Level:
    def __init__(self, tmx_map, level_frames, configs):
        self.configs = configs
        self.display = pygame.display.get_surface()
        self.tmx_map = tmx_map
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.semi_collistion_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.setup(tmx_map, level_frames)

    def setup(self, tmx_map, level_frames):
        # tiles
        for layer in ["BG", "Terrain", "FG", "Platforms"]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == "Terrain": groups.append(self.collision_sprites)
                elif layer == "Platforms": groups.append(self.semi_collistion_sprites)
                match layer:
                    case "BG": z = self.configs.z_layers["bg tiles"]
                    case "FG": z = self.configs.z_layers["fg"]
                    case _: z = self.configs.z_layers["main"]

                z = self.configs.z_layers['bg tiles']
                Sprite((x*64, y*64), surf, groups, z)

        # bg details
        for obj in tmx_map.get_layer_by_name("BG details"):
            if obj.name == "static":
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, z = self.configs.z_layers["bg tiles"])
            else:
                AnimatedSprite((obj.x, obj.y), level_frames[obj.name], self.all_sprites, self.configs.z_layers["bg tiles"])

        # objects
        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "player":
                player_pos = (obj.x, obj.y)
                self.player = Player(player_pos, self.all_sprites, self.collision_sprites, self.semi_collistion_sprites, level_frames["player"], self.configs)
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

                    z = self.configs.z_layers["main"] if not "bg" in obj.name else self.configs.z_layers["bg details"]

                    anim_speed = 6 if not "palm" in obj.name else 6 + uniform(-1, 1)
                    AnimatedSprite((obj.x, obj.y), frames, groups, z, anim_speed)

        
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
                        z = self.configs.z_layers["bg details"],
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
                            Sprite((x, y), level_frames["saw_chain"], self.all_sprites, self.configs.z_layers["bg details"])
                    else:
                        x = start_pos[0] - level_frames["saw_chain"].get_width() // 2
                        top, bottom = int(start_pos[1]), int(end_pos[1])
                        for y in range(top, bottom, 20):
                            Sprite((x, y), level_frames["saw_chain"], self.all_sprites, self.configs.z_layers["bg details"])
                
            # enemies
            # for obj in tmx_map.get_layer_by_name("Enemies"):
            #     if obj.name == "tooth":
            #         Tooth(pos, frames, groups, collision_sprites)

        # items
        for obj in tmx_map.get_layer_by_name("Items"):
            Item(obj.name, (obj.x + 32, obj.y + 32), level_frames["items"][obj.name], (self.all_sprites, self.item_sprites))

        # water
        for obj in tmx_map.get_layer_by_name("Water"):
                rows = int(obj.height / 64)
                cols = int(obj.width / 64)
                for row in range(rows):
                    for col in range(cols):
                        x = obj.x + col * 64
                        y = obj.y + row * 64
                        if row == 0:
                            AnimatedSprite((x, y), level_frames["water_top"], self.all_sprites, self.configs.z_layers["water"])
                        else:
                            Sprite((x, y), level_frames["water_body"], self.all_sprites, self.configs.z_layers["water"])
    
    def item_collision(self):
        if self.item_sprites:
            item_sprites = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            # if item_sprites:
                

    def run(self, dt):
        self.all_sprites.update(dt)
        self.item_collision()
        self.all_sprites.draw(self.player.hitbox_rect.center)