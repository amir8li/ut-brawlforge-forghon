import pygame

class Bullet:
    def __init__(self, game, size):
        self.game = game
        self.pos = [0, 0]
        self.size = size
        self.is_clicked = False
        self.count = 0
        self.direction = ""
        self.angle = 0
    def start(self, player):
        player_rect = player.rect()
        self.pos = list(player_rect.center)
        if player.flip:
            self.direction = "left"
        else:
            self.direction = "right"

    def reset(self):
        self.is_clicked = False
        self.count = 0
        self.direction = ""
        self.pos = [-1000, -1000]  

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, tilemap):
        if self.direction == "left":
            self.pos[0] -= 5
        else:
            self.pos[0] += 5
        bullet_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if bullet_rect.colliderect(rect):
                self.reset()
    

    def render(self, surf, offset=(0, 0)):
        image = self.game.assets["bullet"]
        self.angle += self.game.configs.bullet_angle_change % 360
        rotated_image = pygame.transform.rotate(image, self.angle)
        surf.blit(rotated_image, (self.pos[0] - offset[0], self.pos[1] - offset[1]))