# src/menu/waiting_for_invite.py
import pygame
import os
from config import SCREEN_SIZE, FPS
from src.menu.button import Button

class WaitingForInviteScreen:
    def __init__(self, surface, network, target_id):
        self.surface = surface
        self.network = network
        self.target_id = target_id
        self.clock = pygame.time.Clock()
        
        self.bg = pygame.Surface(SCREEN_SIZE)
        self.bg.fill((20, 20, 40))

        font_path = os.path.join("src", "assets", "images", "menu", "fonts", "runescape_uf.ttf")
        self.font = pygame.font.Font(font_path, 48)
        self.small_font = pygame.font.Font(font_path, 24)

        self.message = f"Invite sent to player..."
        self.sub_message = "Waiting for response..."
        self.game_data = None

    def run(self):
        self.running = True
        while self.running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # TODO: Implement invite cancellation
                    self.network.disconnect()
                    pygame.quit()
                    exit()
            
            # Check for messages from the server
            server_msg = self.network.get_message()
            if server_msg:
                msg_type = server_msg.get("type")
                if msg_type == "invite_accepted":
                    self.sub_message = "Invite Accepted! Starting game..."
                elif msg_type == "invite_declined":
                    self.sub_message = "Invite was declined by the player."
                    pygame.time.delay(2000) # Show message for 2 seconds
                    self.running = False
                elif msg_type == "invite_failed":
                    reason = server_msg.get("data", {}).get("reason", "Unknown error")
                    self.sub_message = f"Invite failed: {reason}"
                    pygame.time.delay(2000)
                    self.running = False
                elif msg_type == "room_created":
                    self.game_data = server_msg['data']
                    self.running = False # Exit the waiting loop
            
            self.draw()

        return self.game_data

    def draw(self):
        self.surface.blit(self.bg, (0, 0))
        
        text_surf = self.font.render(self.message, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 - 50))
        self.surface.blit(text_surf, text_rect)

        sub_surf = self.small_font.render(self.sub_message, True, (200, 200, 200))
        sub_rect = sub_surf.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 20))
        self.surface.blit(sub_surf, sub_rect)
            
        pygame.display.update()