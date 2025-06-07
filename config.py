import pygame

class Configs:
    def __init__(self):
        self.FPS = 60
        self.screen_size = (1280, 720)
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
            "clouds": "clouds",
            "bullet":"shuriken.png",
            "heart_full": "healthbar/full.png",
            "heart_half": "healthbar/half.png",
            "heart_empty": "healthbar/empty.png",
            "enemy_full": "healthbar/enemy_full.png",
            "enemy_half1": "healthbar/enemy_half1.png",
            "enemy_half2": "healthbar/enemy_half2.png",
            "enemy_empty": "healthbar/enemy_empty.png",
            "gameover_image": "game_over.png",
        }

        # tiles settings
        self.tile_size = 64

        # jump settings
        self.gravity = 0.2
        self.max_fall_speed = 10
        self.jump_velocity = 4
        self.movement_speed = 2

        # player settings
        self.player_spawn_pos = (64, 50)
        self.player_size = (8, 15)
        self.max_jump_count = 2
        self.player_anim_offset = (-3, -3)
        self.fall_limit_y = 2000

        # layers
        self.z_layers = {
            "bg": 0,
            "clouds": 1,
            "bg tiles": 2,
            "path": 3,
            "bg details": 4,
            "main": 5,
            "water": 6,
            "fg": 7
        }