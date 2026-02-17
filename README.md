# AI Pathfinder – Blind Search Visualization

> Step-by-step visualization of BFS, DFS, UCS, DLS, IDDFS, and Bidirectional search on a grid with static walls and dynamic obstacles. Python + Pygame.

The GUI shows how each algorithm explores the map step by step and re-plans when dynamic obstacles block the path.

## Requirements

- Python 3.7+
- Pygame

## Setup and run

```bash
pip install -r requirements.txt
python main.py
```

On macOS, if `pip install pygame` fails (missing SDL), install SDL2 first: `brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf`, then use a virtual environment and install pygame inside it.

## How to use

- **SPACE** – Run or pause the selected algorithm.
- **Keys 1–6** – Select algorithm (1=BFS, 2=DFS, 3=UCS, 4=DLS, 5=IDDFS, 6=Bidirectional).
- **ESC** – Quit.

## Project layout

- `main.py` – Pygame GUI, grid state, algorithm selection, dynamic obstacles, re-planning.
- `search_algorithms.py` – BFS, DFS, UCS, DLS, IDDFS, Bidirectional (each yields frontier/explored/path per step).
- `grid.py` – Movement order and neighbor helpers.
