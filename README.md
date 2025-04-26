# Car Racing Game

A simple 2D car racing game built with Pygame where you race against an AI opponent on a circular track.

## Features
- Player-controlled car with realistic movement physics
- AI opponent that follows the track
- Circular racing track with grass and track boundaries
- Collision detection to keep cars on track

## Controls
- **Up Arrow**: Accelerate
- **Down Arrow**: Brake/Reverse
- **Left Arrow**: Turn Left
- **Right Arrow**: Turn Right
- **R**: Reset game
- **Close Window**: Quit game

## Requirements
- Python 3.6+
- Pygame
- NumPy

## Installation

1. Clone this repository:
```bash
git clone https://github.com/[your-username]/car-racing-game.git
cd car-racing-game
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Game
```bash
python game.py
```

## Game Mechanics
- The player controls the red car
- The blue car is controlled by AI
- Cars slow down when going off track
- The AI opponent adjusts its speed based on turn sharpness

## License
This project is open source and available under the MIT License.
