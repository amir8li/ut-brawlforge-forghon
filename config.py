import pygame

class Configs:
    def __init__(self):
        self.FPS = 60
        self.screen_size = (1080, 720)
        self.caption = "Forghoon"
        pygame.font.init()  
        self.game_over_font = pygame.font.SysFont('Arial', 64, 'bold')

        self.assets = {
            "background": "Free Pixel Art Hill/PNG",
            "grass": "inuse/grass",
            "dirt": "inuse/dirt",
            "stone": "tiles/stone",
            "decor": "tiles/decor",
            "large_decor": "tiles/large_decor",
            "player": "player.png",
            "clouds": "clouds",
            "enemy_frames": "enemies",
            "bullet": "shuriken pronta.png",
            "heart_full": "healthbar/full.png",
            "heart_half": "healthbar/half.png",
            "heart_empty": "healthbar/empty.png",
            "enemy_full": "healthbar/enemy_full.png",
            "enemy_half1": "healthbar/enemy_half1.png",
            "enemy_half2": "healthbar/enemy_half2.png",
            "enemy_empty": "healthbar/enemy_empty.png",
            "gameover_image": "game_over.png",
        }

        self.tile_size = 16

        self.gravity = 0.2
        self.max_fall_speed = 10
        self.jump_velocity = 4
        self.movement_speed = 2

        self.player_spawn_pos = (64, 50)
        self.player_size = (8, 15)
        self.max_jump_count = 2

        self.enemy_spawn_pos = (-40, 99)
        self.enemy_size = (18, 18)
        self.left_x_boundary = -168
        self.right_x_boundary = -12
        self.enemy_damage_power = 30

        self.fall_limit_y = 2000

        self.bullet_size = (7, 7)
        self.bullet_range = 300  
        self.bullet_damage = 25
        self.bullet_angle_change = 10