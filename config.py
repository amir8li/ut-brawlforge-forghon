import pygame

class Configs:
    def __init__(self):
        # game settings
        self.FPS = 60
        self.screen_size = (1080, 720)
        self.caption = "Forghoon"
        pygame.font.init()  
        self.game_over_font = pygame.font.SysFont('Arial', 64, 'bold')
        

        # assets paths
        self.assets = {
            "background": "Free Pixel Art Hill/PNG",
            "grass": "inuse/grass",
            "dirt": "inuse/dirt",
            "stone": "tiles/stone",
            "decor": "tiles/decor",
            "large_decor": "tiles/large_decor",
            "clouds": "clouds",
            "bullet":"shuriken.png"
        }

        # tilemap settings
        self.tile_size = 16

        # velocity settings
        self.gravity = 0.2
        self.max_fall_speed = 10
        self.jump_velocity = 4
        self.movement_speed = 2

        # player settings
        self.player_spawn_pos = (64, 50)
        self.player_size = (8, 15)
        self.max_jump_count = 2
        self.player_anim_offset = (-3, -3)

        #enemy settings
        self.enemy_spawn_pos = (-40, 112) 
        self.enemy_size = (16, 16)
        self.left_x_boundary = -168
        self.right_x_boundary = -12
        self.enemy_damage_power = 30

        #bullet settings
        self.bullet_size = (7, 7)
        self.bullet_range = 300  
        self.bullet_damage = 50
        self.bullet_angle_change = 10
