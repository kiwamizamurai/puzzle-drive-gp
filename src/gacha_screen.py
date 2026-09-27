import pyxel

import gacha
import roster_data
import sound
from constants import COL_BLACK, COL_RED, COL_WHITE, COL_YELLOW, GACHA_COST, SCREEN_H, SCREEN_W

REVEAL_FRAMES = 30
MESSAGE_FRAMES = 40


class GachaScreen:
    def __init__(self):
        self.reveal_timer = 0
        self.message_timer = 0
        self.last_pulled = None
        self.message = ""

    def update(self, profile, confirm_pressed):
        if self.message_timer > 0:
            self.message_timer -= 1
        if self.reveal_timer > 0:
            self.reveal_timer -= 1
            return
        if confirm_pressed:
            if profile.currency >= GACHA_COST:
                profile.currency -= GACHA_COST
                driver = gacha.pull_driver()
                profile.add_driver(driver)
                self.last_pulled = driver
                self.reveal_timer = REVEAL_FRAMES
                if driver.rarity >= 4:
                    sound.play_rare_pull()
                else:
                    sound.play_gacha_pull()
            else:
                self.message = "NOT ENOUGH COIN"
                self.message_timer = MESSAGE_FRAMES

    def draw(self, profile):
        pyxel.cls(COL_BLACK)
        pyxel.text(6, 4, f"GACHA   COIN {int(profile.currency)}   COST {GACHA_COST}", COL_WHITE)

        cx, cy = SCREEN_W // 2, SCREEN_H // 2 - 10
        if self.reveal_timer > 0 and self.last_pulled is not None:
            roster_data.draw_icon(self.last_pulled.template_id, cx, cy, 16)
            name = self.last_pulled.name
            pyxel.text(cx - len(name) * 2, cy + 24, name, COL_YELLOW)
        else:
            pyxel.rectb(cx - 20, cy - 20, 40, 40, COL_WHITE)
            pyxel.text(cx - 3, cy - 3, "?", COL_WHITE)

        if self.message_timer > 0:
            pyxel.text(cx - len(self.message) * 2, cy + 40, self.message, COL_RED)

        pyxel.text(6, SCREEN_H - 16, "Z/ENTER:PULL   X:BACK TO GARAGE", COL_WHITE)
