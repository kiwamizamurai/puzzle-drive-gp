import random

import pyxel

import sound
from constants import (
    ATTR_COLORS,
    BASE_ADVANCE,
    CELL_SIZE,
    CHARGE_PER_GROUP,
    COL_GRAY,
    COL_LIME,
    COL_WHITE,
    COL_YELLOW,
    CURRENCY_PER_GROUP,
    GRID_COLS,
    GRID_PIXEL_W,
    GRID_ROWS,
    GRID_X,
    GRID_Y,
    MATCH_MIN,
    MAX_CASCADE_STEPS,
    MOMENTUM_ADVANCE,
    NUM_ATTRS,
    TURN_TIME_LIMIT_FRAMES,
)
from vecmath import clamp


def find_matches(grid):
    rows = len(grid)
    cols = len(grid[0])
    matched = [[False] * cols for _ in range(rows)]

    for r in range(rows):
        run_start = 0
        for c in range(1, cols + 1):
            if c == cols or grid[r][c] != grid[r][run_start]:
                if c - run_start >= MATCH_MIN:
                    for cc in range(run_start, c):
                        matched[r][cc] = True
                run_start = c

    for c in range(cols):
        run_start = 0
        for r in range(1, rows + 1):
            if r == rows or grid[r][c] != grid[run_start][c]:
                if r - run_start >= MATCH_MIN:
                    for rr in range(run_start, r):
                        matched[rr][c] = True
                run_start = r

    return matched


def connected_components(matched, grid):
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    groups = []

    for r in range(rows):
        for c in range(cols):
            if matched[r][c] and not visited[r][c]:
                color = grid[r][c]
                stack = [(r, c)]
                visited[r][c] = True
                cells = []
                while stack:
                    cr, cc = stack.pop()
                    cells.append((cr, cc))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = cr + dr, cc + dc
                        if (
                            0 <= nr < rows
                            and 0 <= nc < cols
                            and matched[nr][nc]
                            and not visited[nr][nc]
                            and grid[nr][nc] == color
                        ):
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                groups.append((color, cells))

    return groups


def apply_gravity_and_refill(grid):
    rows = len(grid)
    cols = len(grid[0])
    for c in range(cols):
        remaining = [grid[r][c] for r in range(rows) if grid[r][c] is not None]
        missing = rows - len(remaining)
        new_vals = [random.randint(0, NUM_ATTRS - 1) for _ in range(missing)] + remaining
        for r in range(rows):
            grid[r][c] = new_vals[r]


def resolve_cascade(grid):
    matches_by_color = {}
    for _ in range(MAX_CASCADE_STEPS):
        matched = find_matches(grid)
        if not any(any(row) for row in matched):
            break
        groups = connected_components(matched, grid)
        for color, cells in groups:
            matches_by_color.setdefault(color, []).append(len(cells))
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if matched[r][c]:
                    grid[r][c] = None
        apply_gravity_and_refill(grid)
    return matches_by_color


def compute_effects(matches_by_color, leader_attr, speed_mult=1.0, luck_mult=1.0):
    charge_idx = (leader_attr + 1) % NUM_ATTRS
    currency_idx = (leader_attr + 2) % NUM_ATTRS
    momentum_a = (leader_attr + 3) % NUM_ATTRS
    momentum_b = (leader_attr + 4) % NUM_ATTRS

    advance = 0.0
    charge = 0
    currency = 0.0

    for color, groups in matches_by_color.items():
        for size in groups:
            if color == leader_attr:
                advance += (BASE_ADVANCE + max(0, size - MATCH_MIN)) * speed_mult
            elif color == charge_idx:
                charge += CHARGE_PER_GROUP
            elif color == currency_idx:
                currency += CURRENCY_PER_GROUP * luck_mult
            elif color == momentum_a or color == momentum_b:
                advance += MOMENTUM_ADVANCE

    return {"advance": advance, "charge": charge, "currency": currency}


class PuzzleGrid:
    def __init__(self, initial_grid=None):
        if initial_grid is not None:
            self.grid = [row[:] for row in initial_grid]
        else:
            self.grid = [
                [random.randint(0, NUM_ATTRS - 1) for _ in range(GRID_COLS)]
                for _ in range(GRID_ROWS)
            ]
        self.cursor_col = GRID_COLS // 2
        self.cursor_row = GRID_ROWS // 2
        self.holding = False
        self.was_holding = False
        self.timer = TURN_TIME_LIMIT_FRAMES
        self.resolved = False
        self.matches_by_color = None

    def update(self, move_col, move_row, hold, force_end=False):
        if self.resolved:
            return
        self.timer -= 1
        self.holding = hold

        if hold and move_col != 0:
            new_col = clamp(self.cursor_col + move_col, 0, GRID_COLS - 1)
            if new_col != self.cursor_col:
                self._swap(self.cursor_row, self.cursor_col, self.cursor_row, new_col)
                self.cursor_col = new_col
        elif move_col != 0:
            self.cursor_col = clamp(self.cursor_col + move_col, 0, GRID_COLS - 1)

        if hold and move_row != 0:
            new_row = clamp(self.cursor_row + move_row, 0, GRID_ROWS - 1)
            if new_row != self.cursor_row:
                self._swap(self.cursor_row, self.cursor_col, new_row, self.cursor_col)
                self.cursor_row = new_row
        elif move_row != 0:
            self.cursor_row = clamp(self.cursor_row + move_row, 0, GRID_ROWS - 1)

        released = self.was_holding and not hold
        self.was_holding = hold

        if released or force_end or self.timer <= 0:
            self.matches_by_color = resolve_cascade(self.grid)
            if self.matches_by_color:
                sound.play_match()
            self.resolved = True

    def _swap(self, r1, c1, r2, c2):
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]

    def draw(self):
        pyxel.rect(GRID_X - 3, GRID_Y - 3, GRID_PIXEL_W + 6, GRID_ROWS * CELL_SIZE + 6, COL_GRAY)
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                color_idx = self.grid[r][c]
                if color_idx is None:
                    continue
                x = GRID_X + c * CELL_SIZE
                y = GRID_Y + r * CELL_SIZE
                col = ATTR_COLORS[color_idx]
                pyxel.circ(x + CELL_SIZE // 2, y + CELL_SIZE // 2, CELL_SIZE // 2 - 2, col)

        cx = GRID_X + self.cursor_col * CELL_SIZE
        cy = GRID_Y + self.cursor_row * CELL_SIZE
        border_col = COL_YELLOW if self.holding else COL_WHITE
        pyxel.rectb(cx, cy, CELL_SIZE, CELL_SIZE, border_col)

        pyxel.rect(GRID_X, GRID_Y - 10, GRID_PIXEL_W, 4, COL_GRAY)
        frac = max(0.0, self.timer / TURN_TIME_LIMIT_FRAMES)
        pyxel.rect(GRID_X, GRID_Y - 10, int(GRID_PIXEL_W * frac), 4, COL_LIME)
