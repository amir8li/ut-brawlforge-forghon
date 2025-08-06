import pygame
import os
from config import SCREEN_SIZE, FPS
from src.menu.button import Button

class OnlineMenu:
    def __init__(self, surface, audio_files, settings, network):
        self.surface = surface
        self.audio_files = audio_files
        self.settings = settings
        self.network = network
        self.clock = pygame.time.Clock()
        
        self.bg = pygame.Surface(SCREEN_SIZE)
        self.bg.fill((169, 153, 139))
        self.pattern = pygame.image.load(os.path.join("src", "assets", "images", "menu", "box.png")).convert_alpha()
        self.pattern = pygame.transform.scale(self.pattern, (600, 550))

        font_path = os.path.join("src", "assets", "images", "menu", "fonts", "runescape_uf.ttf")
        self.font = pygame.font.Font(font_path, 32)
        self.small_font = pygame.font.Font(font_path, 24)
        self.title_font = pygame.font.Font(font_path, 48)

        self.buttons = []
        self.create_buttons()

        self.invite_popup_active = False
        self.inviter_info = {}
        self.popup_buttons = []
        self.game_starting = False

    def create_buttons(self):
        y_start = 250
        self.buttons.append(Button("1 vs 1", (SCREEN_SIZE[0] // 2, y_start), self.font, lambda: self.select("1v1")))
        self.buttons.append(Button("2 vs 2", (SCREEN_SIZE[0] // 2, y_start + 100), self.font, lambda: self.select("2v2")))
        self.buttons.append(Button("INVITE A FRIEND", (SCREEN_SIZE[0] // 2, y_start + 200), self.font, lambda: self.select("invite")))
        self.buttons.append(Button("BACK", (SCREEN_SIZE[0] // 2, y_start + 300), self.font, lambda: self.select("back")))

    def select(self, choice):
        if 'click' in self.audio_files: self.audio_files['click'].play()
        self.choice = choice
        self.running = False

    def handle_invite_response(self, accepted):
        if 'click' in self.audio_files: self.audio_files['click'].play()
        self.network.respond_to_invite(self.inviter_info['inviter_id'], accepted)
        self.invite_popup_active = False
        if accepted:
            self.game_starting = True

    def draw_invite_popup(self):
        popup_rect = pygame.Rect(0, 0, 500, 250)
        popup_rect.center = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
        pygame.draw.rect(self.surface, (50, 50, 70), popup_rect, border_radius=15)
        pygame.draw.rect(self.surface, (200, 200, 220), popup_rect, width=3, border_radius=15)

        inviter_name = self.inviter_info.get('inviter_username', 'Someone')
        text = f"{inviter_name} invites you to a game!"
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(popup_rect.centerx, popup_rect.centery - 50))
        self.surface.blit(text_surf, text_rect)

        for btn in self.popup_buttons:
            btn.draw(self.surface)

    # در کلاس OnlineMenu در فایل src/menu/online_menu.py
    def run(self):
        self.choice = None
        self.running = True
        self.game_data_to_return = None

        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            server_msg = self.network.get_message()
            if server_msg:
                if server_msg['type'] == 'invite_received' and not self.invite_popup_active:
                    self.inviter_info = server_msg['data']
                    self.invite_popup_active = True
                    self.popup_buttons = [
                        Button("ACCEPT", (SCREEN_SIZE[0] // 2 - 100, SCREEN_SIZE[1] // 2 + 50), self.font, lambda: self.handle_invite_response(True), size=(150, 60)),
                        Button("DECLINE", (SCREEN_SIZE[0] // 2 + 100, SCREEN_SIZE[1] // 2 + 50), self.font, lambda: self.handle_invite_response(False), size=(150, 60))
                    ]
                # --- تغییر کلیدی: اگر بازی شروع شد، اطلاعات را ذخیره کن و خارج شو ---
                elif server_msg['type'] == 'room_created' and self.game_starting:
                    self.game_data_to_return = server_msg['data']
                    self.running = False

            self.surface.blit(self.bg, (0, 0))
            pattern_rect = self.pattern.get_rect(center=(SCREEN_SIZE[0] // 2, 400))
            self.surface.blit(self.pattern, pattern_rect)
            title_text = self.title_font.render("Online Lobby", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(SCREEN_SIZE[0] // 2, 150))
            self.surface.blit(title_text, title_rect)
            if not self.invite_popup_active:
                for btn in self.buttons:
                    btn.update(mouse_pos, mouse_pressed)
                    btn.draw(self.surface)
            else:
                for btn in self.buttons:
                    btn.draw(self.surface)
                for btn in self.popup_buttons:
                    btn.update(mouse_pos, mouse_pressed)
                self.draw_invite_popup()
            pygame.display.update()
            
        if self.game_data_to_return:
            return self.game_data_to_return
        return self.choice