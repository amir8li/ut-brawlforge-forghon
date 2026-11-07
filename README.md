# UT Brawlforge

## Project Structure

The following section outlines the main files and directories of the project, along with a brief description of each:

```text
.
├── config.py        # Main game settings and configuration (e.g., screen dimensions, speed, etc.)
├── .git             # Git version control directory (ignore)
├── .gitignore       # Specifies files and directories to be ignored by Git
├── README.md        # Project documentation and guide
├── requirements.txt # List of required libraries and dependencies
├── run_game.py      # Main script used to launch the game
└── src              # Main source code directory
    ├── assets       # Game resources, including images and sounds
    │   ├── images   # Directory containing game images
    │   │   └── .gitkeep # Empty file to preserve the directory in Git
    │   └── sounds   # Directory containing game audio files
    │       └── .gitkeep # Empty file to preserve the directory in Git
    ├── engine       # Core game logic and engine
    │   ├── game.py  # Main classes and functions for gameplay and game management
    │   └── __init__.py # Required for Python to recognize this directory as a package
    └── utils.py     # General-purpose utility functions used throughout the project
```

## File and Directory Descriptions

- **`config.py`**: Contains the game's general settings, including window dimensions, colors, frame rate, and other constants.
- **`.gitignore`**: Specifies which files and directories Git should exclude from the repository. This typically includes temporary files, cache files, and virtual environment directories. No action is required from the user.
- **`README.md`**: The project's documentation file, providing information about the project, installation instructions, execution instructions, and project structure.
- **`requirements.txt`**: Lists all external Python libraries required by the project. It allows dependencies to be installed easily. Any additional packages or libraries used in the project should be listed here, preferably with their respective versions.
- **`run_game.py`**: The main entry point for the game. Running this script launches the game.
- **`src/`**: Contains all the main source code of the game.
  - **`src/assets/`**: Stores images, audio files, and other resources required by the game.
    - **`src/assets/images/`**: Contains the images used in the game.
    - **`src/assets/sounds/`**: Contains the audio files used in the game.
  - **`src/engine/`**: Contains the core logic and functionality of the game.
    - **`src/engine/game.py`**: Expected to contain the main game class, game loop management, event handling, and other essential gameplay components.
  - **`src/utils.py`**: Contains utility functions and helper classes used across different parts of the project. These help reduce code duplication and improve readability.

## Installation and Execution

Follow the steps below to install and run the project:

### 1. Install Dependencies

Install the required libraries using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 2. Run the Game

**Implementation pending.**

Launch the game by executing the `run_game.py` script:

```bash
python run_game.py
```
