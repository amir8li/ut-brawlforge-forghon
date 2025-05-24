import pygame

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.e_type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {"up": False, "down": False, "left": False, "right": False}
        self.flip = False

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {"up": False, "down": False, "left": False, "right": False}

        if movement[0] > 0:
            self.flip = False
        elif movement[0] < 0:
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

    def render(self, surf, offset=(0, 0)):
        image = self.game.assets[self.e_type]
        if self.flip:
            image = pygame.transform.flip(image, True, False)
        surf.blit(image, (self.pos[0] - offset[0], self.pos[1] - offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.jump_count = 0
        self.HP = 100

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)
        if self.collisions["down"]:
            self.jump_count = 0
        if self.game.space_held and self.jump_count == 0:
            self.velocity[1] = -1 * self.game.configs.jump_velocity
            self.jump_count += 1

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "enemy", pos, size)
        self.HP = 100
        self.velocity[0] = 0.5

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)
        self.pos[0] += self.velocity[0]
        if self.pos[0] >= self.game.configs.right_x_boundary:
            self.flip = True
            self.velocity[0] *= - 1
        elif self.pos[0] <= self.game.configs.left_x_boundary:
            self.flip = False
            self.velocity[0] *= - 1

            
        
