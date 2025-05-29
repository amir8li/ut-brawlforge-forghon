from src.engine.game import Game
from config import Configs

if __name__ == "__main__":
    game = Game(Configs())
    game.run()