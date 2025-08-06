import pygame
import os
import pyperclip
from config import SCREEN_SIZE, FPS
from src.menu.button import Button

class InviteScreen:
    def __init__(self, surface, audio_files, settings):
        self.surface = surface
        self.audio_files = audio_files
        self.settings = settings
        self.clock = pygame.time.Clock()
        
        self.bg = pygame.Surface(SCREEN_SIZE)
        self.bg.fill((20, 20, 40))

        font_path = os.path.join("src", "assets", "images", "menu", "fonts", "runescape_uf.ttf")
        self.font = pygame.font.Font(font_path, 36)
        self.small_font = pygame.font.Font(font_path, 24)
        self.title_font = pygame.font.Font(font_path, 48)

        self.input_rect = pygame.Rect(SCREEN_SIZE[0] // 2 - 250, 300, 500, 50)
        self.target_id = ""
        self.active = True
        self.feedback_message = ""
        
        self.invite_button = Button("SEND INVITE", (SCREEN_SIZE[0] // 2, 400), self.font, self.send_invite)
        self.back_button = Button("BACK", (SCREEN_SIZE[0] // 2, 500), self.font, self.go_back)
        self.choice = None

    def go_back(self):
        self.choice = {"action": "back"}
        self.running = False
        
    def send_invite(self):
        if self.target_id.strip():
            self.choice = {"action": "invite", "id": self.target_id.strip()}
            self.running = False
        else:
            self.feedback_message = "Player ID cannot be empty!"

# در کلاس InviteScreen

    def run(self, message=""):
        self.feedback_message = message
        self.running = True
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_rect.collidepoint(event.pos):
                        self.active = True
                    else:
                        self.active = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        try:
                            pasted_text = pyperclip.paste()
                            self.target_id += pasted_text

                            self.target_id = self.target_id[:40] 
                        except pyperclip.PyperclipException:
                            print("Pyperclip could not find a copy/paste mechanism for your system.")
                    
                    elif self.active:
                        if event.key == pygame.K_RETURN:
                            self.send_invite()
                        elif event.key == pygame.K_BACKSPACE:
                            self.target_id = self.target_id[:-1]
                        else:
                            if len(self.target_id) < 40:
                                self.target_id += event.unicode
            
            self.surface.blit(self.bg, (0, 0))
            
            title_text = self.title_font.render("Invite a Friend", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(SCREEN_SIZE[0] // 2, 150))
            self.surface.blit(title_text, title_rect)
            
            prompt_surf = self.font.render("Enter Player ID:", True, (200, 200, 200))
            prompt_rect = prompt_surf.get_rect(midbottom=(self.input_rect.centerx, self.input_rect.top - 10))
            self.surface.blit(prompt_surf, prompt_rect)

            pygame.draw.rect(self.surface, (255, 255, 255), self.input_rect, 2)
            input_surf = self.font.render(self.target_id, True, (255, 255, 255))
            self.surface.blit(input_surf, (self.input_rect.x + 5, self.input_rect.y + 5))

            if self.feedback_message:
                feedback_surf = self.small_font.render(self.feedback_message, True, (255, 100, 100))
                feedback_rect = feedback_surf.get_rect(center=(SCREEN_SIZE[0] // 2, 570))
                self.surface.blit(feedback_surf, feedback_rect)
            
            self.invite_button.update(mouse_pos, mouse_pressed)
            self.invite_button.draw(self.surface)
            self.back_button.update(mouse_pos, mouse_pressed)
            self.back_button.draw(self.surface)

            pygame.display.update()

        return self.choice