import pyxel

from constants import ATTR_BLUE, ATTR_COLORS, ATTR_GREEN, ATTR_PURPLE, ATTR_RED, ATTR_YELLOW, COL_BLACK, COL_WHITE

SHAPE_CIRCLE = 0
SHAPE_TRIANGLE = 1
SHAPE_SQUARE = 2
SHAPE_DIAMOND = 3

TEMPLATES = {
    "novice_red": {"name": "ROOKIE FLARE", "rarity": 2, "attribute": ATTR_RED, "speed": 8, "power": 6, "luck": 5, "shape": SHAPE_TRIANGLE},
    "spark_red": {"name": "SPARK RUNNER", "rarity": 1, "attribute": ATTR_RED, "speed": 6, "power": 5, "luck": 4, "shape": SHAPE_CIRCLE},
    "ember_red": {"name": "EMBER DASH", "rarity": 1, "attribute": ATTR_RED, "speed": 5, "power": 6, "luck": 3, "shape": SHAPE_SQUARE},
    "blaze_red": {"name": "BLAZE FANG", "rarity": 3, "attribute": ATTR_RED, "speed": 10, "power": 9, "luck": 6, "shape": SHAPE_DIAMOND},
    "inferno_red": {"name": "INFERNO KING", "rarity": 5, "attribute": ATTR_RED, "speed": 15, "power": 16, "luck": 9, "shape": SHAPE_DIAMOND},

    "novice_blue": {"name": "AQUA CADET", "rarity": 2, "attribute": ATTR_BLUE, "speed": 7, "power": 6, "luck": 6, "shape": SHAPE_CIRCLE},
    "wave_blue": {"name": "WAVE GLIDER", "rarity": 1, "attribute": ATTR_BLUE, "speed": 6, "power": 4, "luck": 5, "shape": SHAPE_TRIANGLE},
    "tide_blue": {"name": "TIDE RUNNER", "rarity": 1, "attribute": ATTR_BLUE, "speed": 5, "power": 5, "luck": 4, "shape": SHAPE_SQUARE},
    "torrent_blue": {"name": "TORRENT ACE", "rarity": 3, "attribute": ATTR_BLUE, "speed": 9, "power": 8, "luck": 8, "shape": SHAPE_DIAMOND},

    "novice_green": {"name": "LEAF SCOUT", "rarity": 2, "attribute": ATTR_GREEN, "speed": 7, "power": 5, "luck": 7, "shape": SHAPE_SQUARE},
    "vine_green": {"name": "VINE DASHER", "rarity": 1, "attribute": ATTR_GREEN, "speed": 6, "power": 5, "luck": 5, "shape": SHAPE_CIRCLE},
    "moss_green": {"name": "MOSS TRIAL", "rarity": 1, "attribute": ATTR_GREEN, "speed": 5, "power": 4, "luck": 6, "shape": SHAPE_TRIANGLE},
    "forest_green": {"name": "FOREST WARDEN", "rarity": 4, "attribute": ATTR_GREEN, "speed": 11, "power": 10, "luck": 10, "shape": SHAPE_DIAMOND},

    "novice_yellow": {"name": "VOLT PILOT", "rarity": 2, "attribute": ATTR_YELLOW, "speed": 9, "power": 5, "luck": 6, "shape": SHAPE_TRIANGLE},
    "spark_yellow": {"name": "SPARK CUB", "rarity": 1, "attribute": ATTR_YELLOW, "speed": 6, "power": 4, "luck": 5, "shape": SHAPE_SQUARE},
    "thunder_yellow": {"name": "THUNDER ACE", "rarity": 4, "attribute": ATTR_YELLOW, "speed": 12, "power": 9, "luck": 9, "shape": SHAPE_DIAMOND},

    "novice_purple": {"name": "SHADE ROOKIE", "rarity": 2, "attribute": ATTR_PURPLE, "speed": 7, "power": 7, "luck": 5, "shape": SHAPE_CIRCLE},
    "dusk_purple": {"name": "DUSK RIDER", "rarity": 1, "attribute": ATTR_PURPLE, "speed": 5, "power": 6, "luck": 4, "shape": SHAPE_TRIANGLE},
    "eclipse_purple": {"name": "ECLIPSE LORD", "rarity": 5, "attribute": ATTR_PURPLE, "speed": 14, "power": 15, "luck": 11, "shape": SHAPE_DIAMOND},
}

TEMPLATE_IDS = list(TEMPLATES.keys())


def draw_icon(template_id, x, y, r):
    tpl = TEMPLATES[template_id]
    col = ATTR_COLORS[tpl["attribute"]]
    shape = tpl["shape"]

    if shape == SHAPE_CIRCLE:
        pyxel.circ(x, y, r, col)
        pyxel.circb(x, y, r, COL_BLACK)
    elif shape == SHAPE_TRIANGLE:
        pyxel.tri(x, y - r, x - r, y + r, x + r, y + r, col)
        pyxel.trib(x, y - r, x - r, y + r, x + r, y + r, COL_BLACK)
    elif shape == SHAPE_SQUARE:
        pyxel.rect(x - r, y - r, r * 2, r * 2, col)
        pyxel.rectb(x - r, y - r, r * 2, r * 2, COL_BLACK)
    elif shape == SHAPE_DIAMOND:
        pyxel.tri(x, y - r, x - r, y, x, y + r, col)
        pyxel.tri(x, y - r, x + r, y, x, y + r, col)
        pyxel.line(x, y - r, x - r, y, COL_BLACK)
        pyxel.line(x - r, y, x, y + r, COL_BLACK)
        pyxel.line(x, y + r, x + r, y, COL_BLACK)
        pyxel.line(x + r, y, x, y - r, COL_BLACK)

    stars = "*" * tpl["rarity"]
    pyxel.text(x - r, y + r + 2, stars, COL_WHITE)
