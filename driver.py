from constants import LEVEL_CAP
from roster_data import TEMPLATES

_next_instance_id = [0]


def _new_instance_id():
    _next_instance_id[0] += 1
    return _next_instance_id[0]


class Driver:
    def __init__(self, template_id, level=1, xp=0):
        self.instance_id = _new_instance_id()
        self.template_id = template_id
        self.level = level
        self.xp = xp

    def template(self):
        return TEMPLATES[self.template_id]

    @property
    def name(self):
        return self.template()["name"]

    @property
    def rarity(self):
        return self.template()["rarity"]

    @property
    def attribute(self):
        return self.template()["attribute"]

    def _effective(self, base):
        return base + (self.level - 1) * self.rarity * 0.4

    def effective_speed(self):
        return self._effective(self.template()["speed"])

    def effective_power(self):
        return self._effective(self.template()["power"])

    def effective_luck(self):
        return self._effective(self.template()["luck"])

    def xp_to_next(self):
        return 20 + self.level * 10

    def gain_xp(self, amount):
        self.xp += amount
        while self.level < LEVEL_CAP and self.xp >= self.xp_to_next():
            self.xp -= self.xp_to_next()
            self.level += 1
