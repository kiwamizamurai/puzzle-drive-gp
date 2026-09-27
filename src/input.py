import pyxel

BTN_UP = (pyxel.KEY_UP, pyxel.GAMEPAD1_BUTTON_DPAD_UP)
BTN_DOWN = (pyxel.KEY_DOWN, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
BTN_LEFT = (pyxel.KEY_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
BTN_RIGHT = (pyxel.KEY_RIGHT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
BTN_CONFIRM = (pyxel.KEY_Z, pyxel.GAMEPAD1_BUTTON_A)
BTN_START = (pyxel.KEY_RETURN, pyxel.GAMEPAD1_BUTTON_START)
BTN_BACK = (pyxel.KEY_X, pyxel.GAMEPAD1_BUTTON_B)
BTN_GACHA = (pyxel.KEY_C, pyxel.GAMEPAD1_BUTTON_Y)
BTN_SPACE = (pyxel.KEY_SPACE, pyxel.GAMEPAD1_BUTTON_A)


def held(binding):
    key, gamepad_btn = binding
    return pyxel.btn(key) or pyxel.btn(gamepad_btn)


def pressed(binding, hold=None, repeat=None):
    key, gamepad_btn = binding
    return pyxel.btnp(key, hold=hold, repeat=repeat) or pyxel.btnp(
        gamepad_btn, hold=hold, repeat=repeat
    )
