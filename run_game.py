import pygame
import sys

from config import SCREEN_SIZE
from src.engine.game import Game
from src.menu.loading_screen import LoadingScreen
from src.menu.main_menu import MainMenu
from src.menu.mode_selection import ModeSelectScreen
from src.menu.name_input import NameInputScreen
from src.menu.map_char_selection import MapCharacterSelect
from src.menu.end_screen import EndScreen
from src.menu.option_screen import OptionsScreen

def run_game(mode, selected_map, selected_hero, player_names, screen, audio_files, settings):
    while True:
        game = Game(
            mode=mode,
            selected_map=selected_map,
            selected_hero=selected_hero,
            player_names=player_names,
            audio_files=audio_files,
            settings=settings
        )

        result = game.run()
        if result in ["win", "gameover"] or result.endswith("won"):
            snapshot = pygame.display.get_surface().copy()
            end_screen = EndScreen(screen, result, snapshot, audio_files, settings)
            choice = end_screen.run()
            if choice in ["restart", "next"]:
                continue
            elif choice == "menu":
                return "menu"
            else:
                break
        else:
            break

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)

    settings = Game.load_settings()
    audio_files, settings = Game.load_audio_files(settings)

    skip_loading = False  

    while True:
        if not skip_loading:
            LoadingScreen(screen, audio_files).run()
        else:
            skip_loading = False  # فقط برای یک بار از لودینگ رد بشیم

        main_menu = MainMenu(screen, audio_files, settings)
        menu_choice = main_menu.run()

        if menu_choice == "start":
            mode_screen = ModeSelectScreen(screen, audio_files, settings)
            selected_mode = mode_screen.run()

            if selected_mode == "multi":
                name_input = NameInputScreen(screen, audio_files, settings)
                player_names = name_input.run()
            else:
                player_names = ["Player"]

            map_char_select = MapCharacterSelect(
                screen, selected_mode, player_names, audio_files, settings
            )
            selected_map, selected_characters = map_char_select.run()

            result = run_game(
                mode=selected_mode,
                selected_map=selected_map,
                selected_hero=selected_characters,
                player_names=player_names,
                screen=screen,
                audio_files=audio_files,
                settings=settings
            )
            if result == "menu":
                continue

        elif menu_choice == "options":
            options_screen = OptionsScreen(screen, audio_files, settings)
            options_screen.run()

            audio_files["menu_bg"].set_volume(settings.get("music_volume", 0.5))

            skip_loading = True  
            continue

        elif menu_choice == "quit":
            if "menu_bg" in audio_files:
                audio_files["menu_bg"].stop()
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()
