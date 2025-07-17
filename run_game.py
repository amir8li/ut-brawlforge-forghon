import pygame
import sys

from src.menu.loading_screen import LoadingScreen
from src.menu.main_menu import MainMenu
from src.menu.mode_selection import ModeSelectScreen
from src.menu.name_input import NameInputScreen
from src.menu.map_char_selection import MapCharacterSelect
from src.menu.end_screen import EndScreen
from src.engine.game import Game
from config import SCREEN_SIZE

def run_game(mode, selected_map, selected_hero, player_names):
    while True:
        selected_hero_str = selected_hero[0] if isinstance(selected_hero, list) else selected_hero

        game = Game(
            mode=mode,
            selected_map=selected_map,
            selected_hero=selected_hero,
            player_names=player_names
        )
        result = game.run()

        if result in ["win", "gameover"]:
            background_snapshot = pygame.display.get_surface().copy()
            end_screen = EndScreen(pygame.display.get_surface(), result, background_snapshot)
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

    while True:
        loading = LoadingScreen(screen)
        loading.run()

        main_menu = MainMenu(screen)
        menu_choice = main_menu.run()

        if menu_choice == "start":
            mode_screen = ModeSelectScreen(screen)
            selected_mode = mode_screen.run()

            if selected_mode == "multi":
                name_input = NameInputScreen(screen)
                player_names = name_input.run()
            else:
                player_names = ["Player"]

            map_char_select = MapCharacterSelect(screen, selected_mode, player_names)
            selected_map, selected_characters = map_char_select.run()

            result = run_game(
                mode=selected_mode,
                selected_map=selected_map,
                selected_hero=selected_characters,
                player_names=player_names
            )

            if result == "menu":
                continue

        elif menu_choice == "quit":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()
