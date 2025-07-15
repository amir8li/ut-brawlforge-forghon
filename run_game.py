import pygame
from src.menu.loading_screen import LoadingScreen
from src.menu.main_menu import MainMenu
from src.menu.mode_selection import ModeSelectScreen
from src.menu.name_input import NameInputScreen
from src.menu.map_char_selection import MapCharacterSelect
from src.menu.end_screen import EndScreen
from src.engine.game import Game
from config import single_maps, multi_maps
import sys

def run_game(mode, selected_map, selected_hero, player_names):
    while True:
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
            if choice == "restart":
                continue
            elif choice == "next":
                maps = single_maps if mode == "single" else multi_maps
                if selected_map in maps:
                    current_index = maps.index(selected_map)
                    selected_map = maps[(current_index + 1) % len(maps)]
                continue
            else:
                break
        else:
            break

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))

    loading = LoadingScreen(screen)
    loading.run()

    main_menu = MainMenu(screen)
    menu_choice = main_menu.run()

    if menu_choice == "start":
        mode_screen = ModeSelectScreen(screen)
        selected_mode = mode_screen.run()

        player_names = []
        if selected_mode == "multi":
            name_input = NameInputScreen(screen)
            player_names = name_input.run()
        else:
            player_names = ["Player"]

        map_char_select = MapCharacterSelect(screen, selected_mode)
        selected_map, selected_character = map_char_select.run()

        run_game(
            mode=selected_mode,
            selected_map=selected_map,
            selected_hero=selected_character,
            player_names=player_names
        )
    elif menu_choice == "quit":
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
