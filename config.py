class Configs:
    def __init__(self):
        # game settings
        self.FPS = 60
        self.screen_size = (1080, 720)
        self.caption = "Forghoon"

        # assets paths
        self.assets = {
            "background": "Free Pixel Art Hill/PNG",
            "grass": "inuse/grass",
            "dirt": "inuse/dirt",
            "stone": "tiles/stone",
            "decor": "tiles/decor",
            "large_decor": "tiles/large_decor",
            "player": "player.png",
            "clouds": "clouds",
        }

        # tilemap settings
        self.tile_size = 16

        # velocity settings
        self.gravity = 0.2
        self.max_fall_speed = 10
        self.jump_velocity = 4
        self.movement_speed = 2

        # player settings
        self.spawn_pos = (64, 50)
        self.player_size = (8, 15)
        self.max_jump_count = 2
