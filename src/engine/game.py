import pygame
import sys

from src.tilemap import Tilemap
from src.entities import Player, Enemy
from src.utils import load_image, load_images, Animation
from src.clouds import Clouds
from src.bullet import Bullet

class Game:
    def __init__(self, configs):
        pygame.init()
        self.configs = configs
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((configs.screen_size[0], configs.screen_size[1]))
        self.display = pygame.Surface((configs.screen_size[0]//2, configs.screen_size[1]//2))
        pygame.display.set_caption(configs.caption)

        self.assets = {
            "background": load_images(configs.assets["background"], scale=(configs.screen_size[0]//2, configs.screen_size[1]//2)),
            "grass": load_images(configs.assets["grass"]),
            "stone": load_images(configs.assets["stone"]),
            "decor": load_images(configs.assets["decor"]),
            "large_decor": load_images(configs.assets["large_decor"]),
            "clouds": load_images(configs.assets["clouds"]),
            "player/idle": Animation(load_images("player/idle", convert=True), frame_rate=15),
            "player/run": Animation(load_images("player/run", convert=True)),
            "player/jump": Animation(load_images("player/jump", convert=True)),
            "player/slide": Animation(load_images("player/slide", convert=True)),
            "player/wall_slide": Animation(load_images("player/wall_slide", convert=True)),
            "enemy/idle": Animation(load_images("enemy/idle",scale=configs.enemy_size, convert=True)),
            "enemy/run": Animation(load_images("enemy/run", scale=configs.enemy_size, convert=True)),
            "bullet": load_image(configs.assets["bullet"], scale=(configs.bullet_size), convert=True),
            "heart_full": load_image(configs.assets["heart_full"], scale=(15, 15)),
            "heart_half": load_image(configs.assets["heart_half"], scale=(15, 15)),
            "heart_empty": load_image(configs.assets["heart_empty"], scale=(15, 15)),
            "enemy_full": load_image(configs.assets["enemy_full"], scale=(24, 6), convert=True),
            "enemy_half1": load_image(configs.assets["enemy_half1"], scale=(24, 6), convert=True),
            "enemy_half2": load_image(configs.assets["enemy_half2"], scale=(24, 6), convert=True),
            "enemy_empty": load_image(configs.assets["enemy_empty"], scale=(24, 6), convert=True),
            "gameover_image": load_image(configs.assets["gameover_image"], scale=(350, 350)),
        }

        self.assets["heart_full"].set_colorkey((210, 180, 140))
        self.assets["heart_half"].set_colorkey((210, 180, 140))
        self.assets["heart_empty"].set_colorkey((210, 180, 140))

        self.movement = [False, False]
        self.space_held = False
        self.player = Player(self, configs.player_spawn_pos, configs.player_size, configs.player_anim_offset)
        self.player.HP = 100

        self.enemy = Enemy(self, configs.enemy_spawn_pos, configs.enemy_size, configs.enemy_anim_offset)
        self.bullet = Bullet(self, configs.bullet_size)

        self.clouds = Clouds(self.assets["clouds"], count=16)
        self.tilemap = Tilemap(self, tile_size=configs.tile_size)

        self.scroll = [0, 0]
        self.lose = False
        self.enemies_count = 1
        self.score = 0

    def draw_health_hearts(self, surf, current_hp, max_hp, pos):
        heart_full = self.assets["heart_full"]
        heart_half = self.assets["heart_half"]
        heart_empty = self.assets["heart_empty"]

        max_hearts = max_hp // 20
        hp_left = current_hp

        spacing = 5
        for i in range(max_hearts):
            x = pos[0] + i * (heart_full.get_width() + spacing)
            y = pos[1]
            if hp_left >= 20:
                surf.blit(heart_full, (x, y))
                hp_left -= 20
            elif hp_left == 10:
                surf.blit(heart_half, (x, y))
                hp_left -= 10
            else:
                surf.blit(heart_empty, (x, y))

    def draw_health_bar(self, surf, current_hp, max_hp, pos):
        health_bar_empty = self.assets["enemy_empty"]
        health_ratio = current_hp / max_hp

        if health_ratio > 0.75:
            health_bar = self.assets["enemy_full"]
        elif health_ratio > 0.50:
            health_bar = self.assets["enemy_half1"]
        elif health_ratio > 0.25:
            health_bar = self.assets["enemy_half2"]
        else:
            health_bar = self.assets["enemy_empty"]

        surf.blit(health_bar_empty, (pos[0], pos[1]))
        if health_ratio > 0:
            health_bar_width = health_bar.get_width()
            clipped_width = int(health_bar_width * health_ratio)
            clipped_bar = pygame.Surface((clipped_width, health_bar.get_height()), pygame.SRCALPHA)
            clipped_bar.blit(health_bar, (0, 0), (0, 0, clipped_width, health_bar.get_height()))
            surf.blit(clipped_bar, (pos[0], pos[1]))

    def run(self):
        running = True
        while running:
            self.clock.tick(self.configs.FPS)
            for layer in self.assets["background"]:
                self.display.blit(layer, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        self.space_held = True
                        if self.player.jump_count < self.configs.max_jump_count:
                            self.player.velocity[1] = -1 * self.configs.jump_velocity
                            self.player.jump_count += 1
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.bullet.is_clicked = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_SPACE:
                        self.space_held = False

            if self.player.rect().colliderect(self.enemy.rect()):
                self.player.HP -= self.configs.enemy_damage_power
                if self.player.HP <= 0:
                    self.player.HP = 0
                    self.lose = True
                else:
                    self.player.pos = list(self.configs.player_spawn_pos)

            if not self.lose:
                self.scroll[0] += int(self.player.rect().centerx - self.display.get_width() // 2 - self.scroll[0])
                self.scroll[1] += int(self.player.rect().centery - self.display.get_height() // 2 - self.scroll[1])

                self.clouds.update()
                self.clouds.render(self.display, offset=self.scroll)

                self.tilemap.render(self.display, offset=self.scroll)

                self.player.update(self.tilemap, ((self.movement[1] - self.movement[0]) * self.configs.movement_speed, 0))
                self.player.render(self.display, offset=self.scroll)

                if self.bullet.is_clicked:
                    if self.bullet.count == 0:
                        self.bullet.start(self.player)
                        self.bullet.count = 1
                    else:
                        self.bullet.update(self.tilemap)
                    self.bullet.render(self.display, offset=self.scroll)

                if (self.bullet.pos[0] >= self.player.pos[0] + self.configs.bullet_range or
                    self.bullet.pos[0] <= self.player.pos[0] - self.configs.bullet_range):
                    self.bullet.reset()

                if self.bullet.rect().colliderect(self.enemy.rect()):
                    self.bullet.reset()
                    self.enemy.HP -= self.configs.bullet_damage
                    if self.enemy.HP <= 0:
                        self.score += 100

                if self.enemy.HP <= 0:
                    self.enemies_count -= 1
                    self.enemy.remove()
                else:
                    self.enemy.render(self.display, offset=self.scroll)
                    self.enemy.update(self.tilemap, (0, 0))
                    health_bar_pos = (self.enemy.pos[0] - self.scroll[0] - 4, self.enemy.pos[1] - self.scroll[1] - 5)
                    self.draw_health_bar(self.display, self.enemy.HP, 100, health_bar_pos)

                if self.player.pos[1] > self.configs.fall_limit_y:
                    self.lose = True  

            if self.lose:
                self.clouds.render(self.display, offset=self.scroll)
                self.tilemap.render(self.display, offset=self.scroll)
                self.player.render(self.display, offset=self.scroll)
                self.enemy.render(self.display, offset=self.scroll)

                gameover_image = self.assets["gameover_image"]
                gameover_rect = gameover_image.get_rect(center=(self.display.get_width() // 2, self.display.get_height() // 2))
                self.display.blit(gameover_image, gameover_rect)

            self.draw_health_hearts(self.display, self.player.HP, 100, (10, 10))

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()

        pygame.quit()