import pyxel

from board_data import BOARDS
from constants import COL_BLACK, COL_GRAY, COL_WHITE, COL_YELLOW, SCREEN_H, SCREEN_W


def _center_text(text, y, col):
    x = SCREEN_W // 2 - len(text) * 2
    pyxel.text(x + 1, y + 1, text, COL_BLACK)
    pyxel.text(x, y, text, col)


class RaceSelectScreen:
    def __init__(self):
        self.cursor = 0

    def update(self, left, right):
        if left:
            self.cursor = (self.cursor - 1) % len(BOARDS)
        if right:
            self.cursor = (self.cursor + 1) % len(BOARDS)

    def selected_board(self):
        return BOARDS[self.cursor]

    def draw(self, profile):
        pyxel.cls(COL_BLACK)
        _center_text("SELECT RACE", 10, COL_WHITE)

        board = BOARDS[self.cursor]
        box_w, box_h = 150, 60
        box_x = SCREEN_W // 2 - box_w // 2
        box_y = 30
        pyxel.rectb(box_x, box_y, box_w, box_h, COL_WHITE)
        pyxel.rect(box_x + 4, box_y + 4, box_w - 8, box_h - 8, board["theme_col"])

        pyxel.text(box_x - 12, box_y + box_h // 2, "<", COL_WHITE)
        pyxel.text(box_x + box_w + 6, box_y + box_h // 2, ">", COL_WHITE)

        _center_text(board["name"], box_y + box_h + 10, COL_YELLOW)
        _center_text(f"{board['tile_count']} TILES   LV{board['rival_level']} RIVALS", box_y + box_h + 20, COL_WHITE)

        dot_count = len(BOARDS)
        start_x = SCREEN_W // 2 - (dot_count - 1) * 6
        for i in range(dot_count):
            col = COL_YELLOW if i == self.cursor else COL_GRAY
            pyxel.circ(start_x + i * 12, box_y + box_h + 32, 2, col)

        leader = profile.leader()
        if leader is not None:
            _center_text(f"LEADER: {leader.name}", SCREEN_H - 28, COL_WHITE)
        _center_text("ENTER:START   X:BACK", SCREEN_H - 14, COL_WHITE)
