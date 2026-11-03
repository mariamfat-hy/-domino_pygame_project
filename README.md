 # Dominoes – Player vs Computer

A graphical Double-Six Domino game developed using Python and Pygame. Play against a computer opponent through a simple graphical interface.

## Features
- Double-Six domino set (28 tiles).
- Player vs. Computer gameplay.
- Automatic tile dealing.
- Legal move checking on both ends of the board.
- Computer opponent with a rule-based move selection strategy.
- Automatic drawing from the boneyard when no legal move is available.
- Winner detection and score comparison.
- Board scrolling using the left and right arrow keys.

## Technologies
- Python
- Pygame
- Random, OS, Sys, and Typing modules

## Project Structure
- `domino_game_pygame.py`: Main game implementation.
- `images/`: Domino tile images.
- `requirements.txt`: Project dependencies.

## Installation

Install Pygame:

```bash
py -m pip install pygame
```

## How to Run

Run the following command inside the project folder:

```bash
py domino_game_pygame.py
```

## Controls
- Click a domino tile to select it.
- Click **PLAY L** to place it on the left.
- Click **PLAY R** to place it on the right.
- Use the left and right arrow keys to scroll through the board.
- Click **PASS** when passing is allowed.

## Computer Opponent

The computer uses a simple rule-based strategy. It checks its legal moves and chooses the available tile with the highest total pip value.

**Note:** This project uses rule-based decision-making, not Machine Learning.

## Author
Mariam Fathy
