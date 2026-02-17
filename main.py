import random
import pygame
import sys

from grid import get_neighbors
from search_algorithms import bfs, dfs, ucs, dls, iddfs, bidirectional_unified

WINDOW_TITLE = "GOOD  PERFORMANCE  TIME APP"

GRID_ROWS = 20
GRID_COLS = 25
CELL_PX = 28

COLOR_BG = (32, 32, 40)
COLOR_GRID_LINE = (60, 60, 70)
COLOR_START = (80, 200, 120)
COLOR_GOAL = (220, 80, 80)
COLOR_WALL = (50, 50, 55)
COLOR_DYNAMIC_WALL = (180, 100, 50)
COLOR_FRONTIER = (100, 160, 220)
COLOR_EXPLORED = (90, 90, 110)
COLOR_PATH = (255, 220, 100)
COLOR_AGENT = (255, 255, 200)
COLOR_TEXT = (240, 240, 245)

STEP_DELAY_MS = 45
AGENT_MOVE_DELAY_MS = 120
DYNAMIC_SPAWN_PROB = 0.03
DLS_DEPTH_DEFAULT = 25

ALGORITHMS = [
    "BFS",
    "DFS",
    "UCS",
    "DLS",
    "IDDFS",
    "Bidirectional",
]


def make_default_grid(rows, cols):
    walls = set()
    for c in range(1, cols - 1):
        walls.add((0, c))
        walls.add((rows - 1, c))
    for r in range(1, rows - 1):
        walls.add((r, 0))
        walls.add((r, cols - 1))
    mid_r, mid_c = rows // 2, cols // 2
    for i in range(3, 8):
        walls.add((mid_r, mid_c - 3 + i))
    for i in range(2, 6):
        walls.add((mid_r - 2 + i, mid_c + 2))
    start = (1, 1)
    goal = (rows - 2, cols - 2)
    return start, goal, walls


class GameState:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.start, self.goal, self.walls = make_default_grid(rows, cols)
        self.dynamic_walls = set()
        self.algorithm_index = 0
        self.running_search = False
        self.search_gen = None
        self.current_frontier = set()
        self.current_explored = set()
        self.current_path = None
        self.agent_path = None
        self.agent_index = 0
        self.phase = "idle"

    def is_wall(self, r, c):
        return (r, c) in self.walls or (r, c) in self.dynamic_walls

    def is_empty(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return False
        pos = (r, c)
        return pos != self.start and pos != self.goal and pos not in self.walls and pos not in self.dynamic_walls

    def try_spawn_dynamic(self):
        if random.random() > DYNAMIC_SPAWN_PROB:
            return
        empty = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.is_empty(r, c):
                    empty.append((r, c))
        if not empty:
            return
        self.dynamic_walls.add(random.choice(empty))

    def blocks_path(self, pos, path_from_agent):
        if not path_from_agent:
            return False
        return pos in path_from_agent

    def get_agent_position(self):
        if not self.agent_path or self.agent_index >= len(self.agent_path):
            return self.start
        return self.agent_path[self.agent_index]


def draw_cell(screen, font, r, c, state, cell_px, show_labels=False):
    x = c * cell_px
    y = r * cell_px
    rect = pygame.Rect(x, y, cell_px - 1, cell_px - 1)
    pos = (r, c)
    agent_cell = None
    if state.phase == "walking" and state.agent_path and state.agent_index < len(state.agent_path):
        agent_cell = state.agent_path[state.agent_index]
    if pos == agent_cell:
        pygame.draw.rect(screen, COLOR_AGENT, rect)
    elif pos == state.start:
        pygame.draw.rect(screen, COLOR_START, rect)
        if show_labels:
            screen.blit(font.render("S", True, (0, 0, 0)), (x + 6, y + 4))
    elif pos == state.goal:
        pygame.draw.rect(screen, COLOR_GOAL, rect)
        if show_labels:
            screen.blit(font.render("T", True, (255, 255, 255)), (x + 6, y + 4))
    elif pos in state.walls:
        pygame.draw.rect(screen, COLOR_WALL, rect)
    elif pos in state.dynamic_walls:
        pygame.draw.rect(screen, COLOR_DYNAMIC_WALL, rect)
    elif state.current_path and pos in state.current_path:
        pygame.draw.rect(screen, COLOR_PATH, rect)
    elif pos in state.current_frontier:
        pygame.draw.rect(screen, COLOR_FRONTIER, rect)
    elif pos in state.current_explored:
        pygame.draw.rect(screen, COLOR_EXPLORED, rect)
    else:
        pygame.draw.rect(screen, COLOR_BG, rect)
    pygame.draw.rect(screen, COLOR_GRID_LINE, rect, 1)


def run_search_step(state):
    if state.search_gen is None:
        return True
    try:
        step = next(state.search_gen)
        if len(step) == 3:
            state.current_frontier, state.current_explored, state.current_path = step
        else:
            state.current_frontier, state.current_explored, state.current_path = step[0], step[1], step[2]
        if state.current_path is not None:
            state.agent_path = state.current_path
            state.agent_index = 0
            state.search_gen = None
            state.phase = "walking"
            return True
        return False
    except StopIteration:
        state.search_gen = None
        state.phase = "idle"
        return True


def start_algorithm(state):
    start = state.start
    if (state.phase in ("walking", "replanning")) and state.agent_path and state.agent_index < len(state.agent_path):
        start = state.agent_path[state.agent_index]
    is_wall = state.is_wall
    rows, cols = state.rows, state.cols
    goal = state.goal
    idx = state.algorithm_index
    if idx == 0:
        state.search_gen = bfs(start, goal, rows, cols, is_wall)
    elif idx == 1:
        state.search_gen = dfs(start, goal, rows, cols, is_wall)
    elif idx == 2:
        state.search_gen = ucs(start, goal, rows, cols, is_wall)
    elif idx == 3:
        state.search_gen = dls(start, goal, rows, cols, is_wall, DLS_DEPTH_DEFAULT)
    elif idx == 4:
        state.search_gen = iddfs(start, goal, rows, cols, is_wall)
    elif idx == 5:
        state.search_gen = bidirectional_unified(start, goal, rows, cols, is_wall)
    else:
        state.search_gen = None
        return
    state.current_frontier = set()
    state.current_explored = set()
    state.current_path = None
    state.phase = "searching"


def main():
    pygame.init()
    width = GRID_COLS * CELL_PX
    height = GRID_ROWS * CELL_PX + 36
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(WINDOW_TITLE)
    font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    state = GameState(GRID_ROWS, GRID_COLS)
    last_step_time = 0
    last_walk_time = 0

    while True:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    if state.phase == "idle":
                        start_algorithm(state)
                    elif state.phase == "searching":
                        state.phase = "idle"
                        state.search_gen = None
                if state.phase == "idle":
                    if event.key == pygame.K_1:
                        state.algorithm_index = 0
                    elif event.key == pygame.K_2:
                        state.algorithm_index = 1
                    elif event.key == pygame.K_3:
                        state.algorithm_index = 2
                    elif event.key == pygame.K_4:
                        state.algorithm_index = 3
                    elif event.key == pygame.K_5:
                        state.algorithm_index = 4
                    elif event.key == pygame.K_6:
                        state.algorithm_index = 5

        if state.phase == "searching":
            if now - last_step_time >= STEP_DELAY_MS:
                last_step_time = now
                run_search_step(state)
        elif state.phase == "walking" and state.agent_path:
            if now - last_walk_time >= AGENT_MOVE_DELAY_MS:
                last_walk_time = now
                state.try_spawn_dynamic()
                remaining_path = state.agent_path[state.agent_index + 1:]
                if state.get_agent_position() == state.goal:
                    state.phase = "idle"
                    state.agent_path = None
                else:
                    next_cell = state.agent_path[state.agent_index + 1] if state.agent_index + 1 < len(state.agent_path) else None
                    blocked = next_cell is not None and state.is_wall(next_cell[0], next_cell[1])
                    if not blocked:
                        for pos in state.dynamic_walls:
                            if state.blocks_path(pos, remaining_path):
                                blocked = True
                                break
                    if blocked:
                        state.phase = "replanning"
                        start_algorithm(state)
                        state.phase = "searching"
                    else:
                        state.agent_index += 1
                        if state.agent_index >= len(state.agent_path):
                            state.phase = "idle"
                            state.agent_path = None

        screen.fill(COLOR_BG)
        for r in range(state.rows):
            for c in range(state.cols):
                draw_cell(screen, font, r, c, state, CELL_PX, show_labels=True)
        menu = "  ".join(
            ("[%d] %s" % (i + 1, ALGORITHMS[i]) if i == state.algorithm_index else "%d %s" % (i + 1, ALGORITHMS[i])
            for i in range(len(ALGORITHMS))
        )
        screen.blit(font.render("Algo: " + menu, True, COLOR_TEXT), (8, GRID_ROWS * CELL_PX + 8))
        screen.blit(font.render("SPACE: Run / Pause   Keys 1-6: Select algorithm", True, COLOR_TEXT), (8, GRID_ROWS * CELL_PX + 24))
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
