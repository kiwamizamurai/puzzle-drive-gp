import random

from constants import GACHA_TABLE
from driver import Driver
from roster_data import TEMPLATES

_CANDIDATES_BY_RARITY = {}
for _template_id, _tpl in TEMPLATES.items():
    _CANDIDATES_BY_RARITY.setdefault(_tpl["rarity"], []).append(_template_id)


def pull_template_id():
    roll = random.random()
    cumulative = 0.0
    chosen_rarity = GACHA_TABLE[-1][0]
    for rarity, prob in GACHA_TABLE:
        cumulative += prob
        if roll <= cumulative:
            chosen_rarity = rarity
            break
    candidates = _CANDIDATES_BY_RARITY[chosen_rarity]
    return random.choice(candidates)


def pull_driver():
    return Driver(pull_template_id())
