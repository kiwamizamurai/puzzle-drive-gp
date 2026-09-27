import pyxel

import roster_data
from constants import COL_BLACK, COL_GRAY, COL_WHITE, COL_YELLOW, SCREEN_H, SCREEN_W
from vecmath import clamp

VISIBLE_ROWS = 7
ROW_H = 14
LIST_Y = 20


class GarageScreen:
    def __init__(self):
        self.cursor = 0

    def update(self, profile, up, down):
        n = len(profile.owned_drivers)
        if n == 0:
            return
        if up:
            self.cursor = (self.cursor - 1) % n
        if down:
            self.cursor = (self.cursor + 1) % n
        self.cursor = clamp(self.cursor, 0, n - 1)

    def current_driver(self, profile):
        if not profile.owned_drivers:
            return None
        idx = clamp(self.cursor, 0, len(profile.owned_drivers) - 1)
        return profile.owned_drivers[idx]

    def draw(self, profile):
        pyxel.cls(COL_BLACK)
        pyxel.text(6, 4, f"GARAGE   COIN {int(profile.currency)}", COL_WHITE)

        n = len(profile.owned_drivers)
        start = clamp(self.cursor - VISIBLE_ROWS // 2, 0, max(0, n - VISIBLE_ROWS))
        end = min(n, start + VISIBLE_ROWS)

        for row, idx in enumerate(range(start, end)):
            d = profile.owned_drivers[idx]
            y = LIST_Y + row * ROW_H
            tag = ""
            if d.instance_id == profile.leader_id:
                tag = "LEADER"
            elif d.instance_id in profile.sub_ids:
                tag = "SUB"
            col = COL_YELLOW if idx == self.cursor else COL_WHITE
            roster_data.draw_icon(d.template_id, 16, y + 5, 6)
            pyxel.text(30, y + 2, f"{d.name} Lv{d.level} {tag}", col)

        d = self.current_driver(profile)
        if d is not None:
            stats = f"SPD {d.effective_speed():.1f}  PWR {d.effective_power():.1f}  LUK {d.effective_luck():.1f}"
            pyxel.text(6, LIST_Y + VISIBLE_ROWS * ROW_H + 6, stats, COL_WHITE)
            xp_line = f"XP {d.xp}/{d.xp_to_next()}"
            pyxel.text(6, LIST_Y + VISIBLE_ROWS * ROW_H + 16, xp_line, COL_GRAY)

        pyxel.text(6, SCREEN_H - 16, "Z:LEADER  X:SUB  C:GACHA  ENTER:RACE", COL_GRAY)
