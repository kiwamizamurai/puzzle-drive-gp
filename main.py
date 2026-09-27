import pyxel

import sound
from app import App
from constants import FPS, SCREEN_H, SCREEN_W

pyxel.init(SCREEN_W, SCREEN_H, title="PUZZLE DRIVE GP", fps=FPS)
sound.init_sounds()

app = App()
pyxel.run(app.update, app.draw)
