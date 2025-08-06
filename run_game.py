import pygame
import sys
from os.path import join

from config import SCREEN_SIZE
from src.engine.game import Game
from src.menu.loading_screen import LoadingScreen
from src.menu.main_menu import MainMenu
from src.menu.mode_selection import ModeSelectScreen
from src.menu.map_char_selection import MapCharacterSelect
from src.menu.end_screen import EndScreen
from src.menu.option_screen import OptionsScreen
from src.menu.name_input import NameInputScreen
from src.menu.name_input_online import NameInputOnlineScreen
from src.client.network import Network
from src.menu.online_menu import OnlineMenu
from src.menu.waiting_room import WaitingRoom
from src.menu.invite_screen import InviteScreen
from src.menu.waiting_for_invite import WaitingForInviteScreen

def run_game(mode, selected_map, selected_hero, player_names, screen, audio_files, settings, network=None, online_game_data=None):
    
    initial_game = Game(
        mode=mode, selected_map=selected_map, selected_hero=selected_hero,
        player_names=player_names, screen=screen, audio_files=audio_files, settings=settings,
        network=network, online_game_data=online_game_data
    )
    initial_result = initial_game.run()

    if initial_result == "start_boss_sequence":
        current_boss_level = 1
        max_boss_levels = 5

        while current_boss_level <= max_boss_levels:
            
            boss_map_path = join("data", "levels", f"boss {current_boss_level}.tmx")
            print(f"--- Starting Boss Level {current_boss_level} ---")

            boss_game = Game(
                mode=mode, selected_map=boss_map_path, selected_hero=selected_hero,
                player_names=player_names, screen=screen, audio_files=audio_files, settings=settings,
                current_level=current_boss_level 
            )
            boss_result = boss_game.run()
            snapshot = pygame.display.get_surface().copy()

            if boss_result == "gameover":
                end_screen = EndScreen(screen, "gameover", snapshot, audio_files, settings)
                choice = end_screen.run()
                if choice == "restart":
                    current_boss_level = 1 
                    continue
                return "menu" 
            
            elif boss_result == "win":
                if current_boss_level == max_boss_levels:
                    end_screen = EndScreen(screen, "final_victory", snapshot, audio_files, settings)
                    choice = end_screen.run() 
                    if choice == "restart":
                        current_boss_level = 1
                        continue
                    return "menu"
                else:
                    end_screen = EndScreen(screen, "win", snapshot, audio_files, settings)
                    choice = end_screen.run() 
                    if choice == "next":
                        current_boss_level += 1
                        continue
                    elif choice == "restart":
                        current_boss_level = 1
                        continue
                    return "menu"
        return "menu" 

    elif initial_result in ["win", "gameover"] or (isinstance(initial_result, str) and initial_result.endswith("won")):
        snapshot = pygame.display.get_surface().copy()
        end_screen = EndScreen(screen, initial_result, snapshot, audio_files, settings)
        choice = end_screen.run()
        if mode == 'online':
             return "menu"
        if choice in ["restart", "next"]:
            return run_game(mode, selected_map, selected_hero, player_names, screen, audio_files, settings)
        elif choice == "menu":
            return "menu"
        else: 
            pygame.quit()
            sys.exit()

    return "menu" 

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Brawlforge")

    CHARACTER_FOLDER_NAMES = [
        "player1",
        "player3",
        "player4",
        "player6"
    ]

    settings = Game.load_settings()
    audio_files, settings = Game.load_audio_files(settings)

    skip_loading = False
    network = None

    while True:
        if not skip_loading:
            LoadingScreen(screen, audio_files).run()
        else:
            skip_loading = False

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
            selected_map_filename, selected_characters = map_char_select.run()
            
            full_map_path = join("data", "levels", selected_map_filename)
            
            result = run_game(
                mode=selected_mode,
                selected_map=full_map_path, 
                selected_hero=selected_characters,
                player_names=player_names,
                screen=screen,
                audio_files=audio_files,
                settings=settings
            )
            
            if result == "menu":
                continue 

        elif menu_choice == "online":
            name_input_screen = NameInputOnlineScreen(screen, audio_files, settings)
            username_list = name_input_screen.run()
            if not username_list or not username_list[0].strip():
                continue
            username = username_list[0]
            
            network = Network()
            player_id = network.connect(username)
            if not player_id:
                print("Could not connect to the server. Is the server running?")
                continue

            online_menu = OnlineMenu(screen, audio_files, settings, network)
            online_choice_or_data = online_menu.run()

            game_data = None
            
            if isinstance(online_choice_or_data, dict):
                game_data = online_choice_or_data
            
            elif online_choice_or_data in ["1v1", "2v2"]:
                network.join_waiting_room(online_choice_or_data)
                waiting_screen = WaitingRoom(screen, network, online_choice_or_data)
                game_data = waiting_screen.run()
            elif online_choice_or_data == "invite":
                invite_page = InviteScreen(screen, audio_files, settings)
                invite_choice = invite_page.run()
                if invite_choice and invite_choice["action"] == "invite":
                    target_id = invite_choice["id"]
                    network.send_invite(target_id)
                    wait_screen = WaitingForInviteScreen(screen, network, target_id)
                    game_data = wait_screen.run()
                else:
                    continue 
            elif online_choice_or_data == "back":
                if network: network.disconnect()
                network = None
                continue

            if game_data:
                online_map = "map1.tmx" if game_data['game_mode'] == "1v1" else "map2.tmx"
                full_map_path = join("data", "levels", online_map)
                all_player_ids = game_data['players']
                
                selected_hero_names = [CHARACTER_FOLDER_NAMES[i] for i in range(len(all_player_ids))]
                
                result = run_game(
                    mode='online',
                    selected_map=full_map_path,
                    selected_hero=selected_hero_names,
                    player_names=[username],
                    screen=screen,
                    audio_files=audio_files,
                    settings=settings,
                    network=network,
                    online_game_data=game_data
                )
                if result == "menu":
                    if network: network.disconnect()
                    network = None
                    continue
            else:
                 continue
                 
        elif menu_choice == "options":
            options_screen = OptionsScreen(screen, audio_files, settings)
            options_screen.run()
            
            if "menu_bg" in audio_files:
                audio_files["menu_bg"].set_volume(settings.get("music_volume", 0.5))

            skip_loading = True
            continue 

        elif menu_choice == "quit":
            if network: network.disconnect()
            if "menu_bg" in audio_files:
                audio_files["menu_bg"].stop()
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()