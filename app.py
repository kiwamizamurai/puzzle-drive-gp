import pyxel

import sound
from constants import (
    COL_BLACK,
    COL_DARKBLUE,
    COL_GRAY,
    COL_RED,
    COL_WHITE,
    COL_YELLOW,
    SCREEN_H,
    SCREEN_W,
    STATE_GACHA,
    STATE_GARAGE,
    STATE_RACE,
    STATE_RACE_SELECT,
    STATE_RESULT,
    STATE_TITLE,
)
from gacha_screen import GachaScreen
from garage import GarageScreen
from player_profile import PlayerProfile
from race import Race
from race_select import RaceSelectScreen


def _center_text(text, y, col, shadow=True):
    x = SCREEN_W // 2 - len(text) * 2
    if shadow:
        pyxel.text(x + 1, y + 1, text, COL_BLACK)
    pyxel.text(x, y, text, col)


class App:
    def __init__(self):
        self.state = STATE_TITLE
        self.profile = PlayerProfile()
        self.garage = GarageScreen()
        self.gacha_screen = GachaScreen()
        self.race_select = RaceSelectScreen()
        self.race = None
        self.blink = 0
        sound.play_bgm()

    def update(self):
        self.blink = (self.blink + 1) % 60
        if self.state == STATE_TITLE:
            self._update_title()
        elif self.state == STATE_GARAGE:
            self._update_garage()
        elif self.state == STATE_GACHA:
            self._update_gacha()
        elif self.state == STATE_RACE_SELECT:
            self._update_race_select()
        elif self.state == STATE_RACE:
            self._update_race()
        elif self.state == STATE_RESULT:
            self._update_result()

    def _update_title(self):
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
            sound.play_menu()
            self.state = STATE_GARAGE

    def _update_garage(self):
        up = pyxel.btnp(pyxel.KEY_UP, hold=10, repeat=4)
        down = pyxel.btnp(pyxel.KEY_DOWN, hold=10, repeat=4)
        self.garage.update(self.profile, up, down)

        if pyxel.btnp(pyxel.KEY_Z):
            d = self.garage.current_driver(self.profile)
            if d is not None:
                self.profile.set_leader(d.instance_id)
                sound.play_menu()
        if pyxel.btnp(pyxel.KEY_X):
            d = self.garage.current_driver(self.profile)
            if d is not None:
                self.profile.toggle_sub(d.instance_id)
                sound.play_menu()
        if pyxel.btnp(pyxel.KEY_C):
            sound.play_menu()
            self.state = STATE_GACHA
        if pyxel.btnp(pyxel.KEY_RETURN):
            sound.play_menu()
            self.state = STATE_RACE_SELECT

    def _update_gacha(self):
        confirm = pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_RETURN)
        self.gacha_screen.update(self.profile, confirm)
        if pyxel.btnp(pyxel.KEY_X):
            sound.play_menu()
            self.state = STATE_GARAGE

    def _update_race_select(self):
        left = pyxel.btnp(pyxel.KEY_LEFT)
        right = pyxel.btnp(pyxel.KEY_RIGHT)
        self.race_select.update(left, right)
        if left or right:
            sound.play_menu()
        if pyxel.btnp(pyxel.KEY_X):
            sound.play_menu()
            self.state = STATE_GARAGE
        if pyxel.btnp(pyxel.KEY_RETURN):
            sound.play_menu()
            board_config = self.race_select.selected_board()
            self.race = Race(board_config, self.profile)
            self.state = STATE_RACE

    def _update_race(self):
        move_col = 0
        move_row = 0
        if pyxel.btnp(pyxel.KEY_LEFT, hold=8, repeat=4):
            move_col = -1
        elif pyxel.btnp(pyxel.KEY_RIGHT, hold=8, repeat=4):
            move_col = 1
        if pyxel.btnp(pyxel.KEY_UP, hold=8, repeat=4):
            move_row = -1
        elif pyxel.btnp(pyxel.KEY_DOWN, hold=8, repeat=4):
            move_row = 1
        hold = pyxel.btn(pyxel.KEY_Z)
        force_end = pyxel.btnp(pyxel.KEY_X)

        aim_dir = 0
        if pyxel.btn(pyxel.KEY_LEFT):
            aim_dir = -1
        elif pyxel.btn(pyxel.KEY_RIGHT):
            aim_dir = 1
        charging = pyxel.btn(pyxel.KEY_Z)

        self.race.update(move_col, move_row, hold, force_end, aim_dir, charging)
        if self.race.finished:
            self.state = STATE_RESULT

    def _update_result(self):
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_Z):
            sound.play_menu()
            self.race = None
            self.state = STATE_GARAGE

    def draw(self):
        if self.state == STATE_TITLE:
            self._draw_title()
        elif self.state == STATE_GARAGE:
            self.garage.draw(self.profile)
        elif self.state == STATE_GACHA:
            self.gacha_screen.draw(self.profile)
        elif self.state == STATE_RACE_SELECT:
            self.race_select.draw(self.profile)
        elif self.state == STATE_RACE:
            self.race.draw()
        elif self.state == STATE_RESULT:
            self._draw_result()

    def _draw_title(self):
        pyxel.cls(COL_DARKBLUE)
        pyxel.rect(0, 50, SCREEN_W, 36, COL_RED)
        pyxel.rectb(0, 50, SCREEN_W, 36, COL_WHITE)
        _center_text("PUZZLE DRIVE GP", 60, COL_YELLOW)
        _center_text("MATCH. FLICK. COLLECT.", 74, COL_WHITE)
        if self.blink < 40:
            _center_text("PRESS ENTER", 116, COL_WHITE)
        _center_text("ARROWS:MOVE  Z:HOLD/CHARGE  X:BACK  C:GACHA", 156, COL_GRAY)

    def _draw_result(self):
        pyxel.cls(COL_BLACK)
        _center_text("RESULT", 10, COL_WHITE)
        if self.race is not None:
            _center_text(f"RANK {self.race.result_rank} / 4", 40, COL_YELLOW)
            _center_text(f"COIN +{self.race.result_currency_gain}", 58, COL_WHITE)
            _center_text(f"XP +{self.race.result_xp_gain}", 70, COL_WHITE)
        leader = self.profile.leader()
        if leader is not None:
            _center_text(f"{leader.name}  Lv{leader.level}", 92, COL_WHITE)
        _center_text("PRESS ENTER TO CONTINUE", SCREEN_H - 14, COL_WHITE)
