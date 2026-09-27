from constants import STARTER_CURRENCY, STARTER_TEMPLATE_ID, SUB_STAT_BONUS
from driver import Driver


class PlayerProfile:
    def __init__(self):
        self.currency = STARTER_CURRENCY
        starter = Driver(STARTER_TEMPLATE_ID)
        self.owned_drivers = [starter]
        self.leader_id = starter.instance_id
        self.sub_ids = []
        self.races_completed = 0

    def get_driver(self, instance_id):
        for d in self.owned_drivers:
            if d.instance_id == instance_id:
                return d
        return None

    def leader(self):
        return self.get_driver(self.leader_id)

    def subs(self):
        return [d for d in (self.get_driver(i) for i in self.sub_ids) if d is not None]

    def add_driver(self, driver):
        self.owned_drivers.append(driver)

    def set_leader(self, instance_id):
        self.leader_id = instance_id
        self.sub_ids = [i for i in self.sub_ids if i != instance_id]

    def toggle_sub(self, instance_id):
        if instance_id == self.leader_id:
            return
        if instance_id in self.sub_ids:
            self.sub_ids.remove(instance_id)
        elif len(self.sub_ids) < 2:
            self.sub_ids.append(instance_id)

    def team_effective_stats(self):
        leader = self.leader()
        if leader is None:
            return 0.0, 0.0, 0.0
        speed = leader.effective_speed()
        power = leader.effective_power()
        luck = leader.effective_luck()
        for sub in self.subs():
            speed += sub.effective_speed() * SUB_STAT_BONUS
            power += sub.effective_power() * SUB_STAT_BONUS
            luck += sub.effective_luck() * SUB_STAT_BONUS
        return speed, power, luck
