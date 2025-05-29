import pygame

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size, anim_offset=(0, 0)):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {"up": False, "down": False, "left": False, "right": False}
        self.flip = False

        self.action = ""
        self.anim_offset = anim_offset
        self.sef_action("idle")

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def sef_action(self, action):
        if action != self.action:
            self.action = action
            self.anim = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {"up": False, "down": False, "left": False, "right": False}

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions["right"] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions["left"] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                self.pos[1] = entity_rect.y

        self.velocity[1] = min(self.game.configs.max_fall_speed, self.velocity[1] + self.game.configs.gravity)

        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0

        self.anim.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.anim.get_current_image(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size, anim_offset=(0, 0)):
        super().__init__(game, "player", pos, size, anim_offset)
        self.air_time = 0
        self.jump_count = 0
        self.HP = 100

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)

        self.air_time += 1
        if self.collisions["down"]:
            self.jump_count = 0
            self.air_time = 0
        if self.game.space_held and self.jump_count == 0:
            self.velocity[1] = -1 * self.game.configs.jump_velocity
            self.jump_count += 1
        
        if self.air_time > 4:
            self.sef_action("jump")
        elif movement[0] != 0:
            self.sef_action("run")
        else:
            self.sef_action("idle")

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size, anim_offset=(0, 0)):
        super().__init__(game, "enemy", pos, size, anim_offset)
        self.HP = 100
        self.velocity[0] = 0.25

    def update(self, tilemap, movement=(0, 0)):
        frame_movement = (movement[0] + self.velocity[0], 0)
        super().update(tilemap, frame_movement)
        self.collisions = {"up": False, "down": False, "left": False, "right": False}

        if frame_movement[0] != 0:
            self.sef_action("run")
        else:
            self.sef_action("idle")

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions["right"] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions["left"] = True
                self.pos[0] = entity_rect.x

        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if entity_rect.bottom > rect.top and entity_rect.bottom <= rect.top + 5:
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                    self.pos[1] = entity_rect.y
                if entity_rect.top < rect.bottom and entity_rect.top >= rect.bottom - 5:
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True
                    self.pos[1] = entity_rect.y

        self.pos[0] += self.velocity[0]
        if self.pos[0] >= self.game.configs.right_x_boundary:
            self.velocity[0] *= -1
        elif self.pos[0] <= self.game.configs.left_x_boundary:
            self.velocity[0] *= -1

    def remove(self):
        self.pos = [-1000, -1000]
        self.velocity = [0, 0] 
        self.HP = 0