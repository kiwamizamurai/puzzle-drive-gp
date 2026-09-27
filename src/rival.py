import random

from constants import REFERENCE_SPEED, RIVAL_BASE_ADVANCE


class Rival:
    def __init__(self, racer_id, driver, color):
        self.racer_id = racer_id
        self.driver = driver
        self.color = color

    def simulated_advance(self):
        speed = self.driver.effective_speed()
        return RIVAL_BASE_ADVANCE * (speed / REFERENCE_SPEED) * random.uniform(0.6, 1.4)
