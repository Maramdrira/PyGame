# 🎮 Puzzle & Game Collection (Pygame)

A polished, integrated desktop application featuring four classic games built with **Pygame**. This project showcases strong software architecture, a custom UI, and a deep understanding of game development fundamentals.


## ✨ Features

### 🧩 1. Sliding Puzzle
*   Dynamic grid sizes (3x3 and 4x4).
*   Custom image upload support (via Tkinter/PIL).
*   Move counter and timer.
*   Interactive image selection carousel.

### 🖼️ 2. Jigsaw Puzzle
*   Algorithmic image splitting into interlocking pieces.
*   Drag-and-drop gameplay with "snap-to-place" validation.
*   Scrollable piece carousel and image preview mode.
*   Timer and completion detection.

### 🔢 3. Sudoku
*   **Self-contained engine** that generates valid puzzles of varying difficulty.
*   Real-time puzzle validation and error checking.
*   Clean, responsive grid with a built-in timer.
*   "New Game," "Check," and "Solve" features.

### 🐍 4. Snake Game
*   Modern take on the classic arcade game.
*   **Particle effects** for food consumption and collisions.
*   Dynamic difficulty: speed increases with score.
*   Temporary obstacles that appear after a high score, adding strategic depth.

### 🎯 Central Launcher
*   A unified menu to seamlessly switch between all four games.
*   Consistent, clean UI with hover effects and custom fonts.
*   Robust error handling for missing assets.

## 🛠️ Tech Stack & Architecture

*   **Language:** Python 3.9+
*   **Game Framework:** Pygame
*   **UI Dialogs:** Tkinter
*   **Image Processing:** PIL/Pillow (for image uploads and thumbnails)
*   **Architecture:** Multi-module application with a central entry point (`main.py`) and separate, self-contained game classes.
*   **Asset Management:** Custom font and sound loading with fallbacks.


## 🕹️ How to Play

1.  Launch the application with `python main.py`.
2.  Use your mouse to select one of the four games from the main menu.
3.  Follow the in-game instructions:
    *   **Sliding Puzzle:** Click on a tile adjacent to the empty space to move it. Arrange the tiles in order.
    *   **Jigsaw Puzzle:** Drag pieces from the carousel at the bottom and place them in the correct position on the board.
    *   **Sudoku:** Click a cell and press a number key (1-9) to fill it in. Press `0`, `Backspace`, or `Delete` to clear a cell.
    *   **Snake:** Use the **Arrow Keys** to control the snake. Eat the red food to grow and avoid obstacles and yourself!

