import pygame
import os
from config import SCREEN_SIZE, FPS

class WaitingRoom:
    def __init__(self, surface, network, game_mode):
        self.surface = surface
        self.network = network
        self.game_mode = game_mode
        self.clock = pygame.time.Clock()
        
        self.bg = pygame.Surface(SCREEN_SIZE)
        self.bg.fill((20, 20, 40)) # Dark blue background

        font_path = os.path.join("src", "assets", "images", "menu", "fonts", "runescape_uf.ttf")
        self.font = pygame.font.Font(font_path, 48)
        self.small_font = pygame.font.Font(font_path, 24)

        self.message = "Waiting for other players..."
        self.countdown_message = ""
        self.game_data = None

    def run(self):
        self.running = True
        while self.running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.network.disconnect()
                    pygame.quit()
                    exit()
            
            # Check for messages from the server
            server_msg = self.network.get_message()
            if server_msg:
                msg_type = server_msg.get("type")
                if msg_type == "room_created":
                    self.message = "Game Found! Starting soon..."
                    self.game_data = server_msg['data']
                elif msg_type == "countdown":
                    seconds = server_msg['data']['seconds']
                    self.countdown_message = f"Starting in {seconds}..."
                elif msg_type == "game_start":
                    self.running = False # Exit the waiting room loop
            
            self.draw()

        return self.game_data

    def draw(self):
        self.surface.blit(self.bg, (0, 0))
        
        # Main message
        text_surf = self.font.render(self.message, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 - 50))
        self.surface.blit(text_surf, text_rect)

        # Countdown message
        if self.countdown_message:
            countdown_surf = self.small_font.render(self.countdown_message, True, (200, 200, 200))
            countdown_rect = countdown_surf.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 20))
            self.surface.blit(countdown_surf, countdown_rect)
            
        pygame.display.update()