import pyxel

from constants import COL_BLACK, COL_GRAY, COL_WHITE


class Board:
    def __init__(self, tile_count, name, theme_col):
        self.tile_count = tile_count
        self.name = name
        self.theme_col = theme_col
        self.positions = {}
        self.finished_turn = {}
        self.stun_turns = {}

    def register(self, racer_id):
        self.positions[racer_id] = 0.0
        self.finished_turn[racer_id] = None
        self.stun_turns[racer_id] = 0

    def advance(self, racer_id, amount):
        if self.finished_turn.get(racer_id) is not None:
            return
        if self.stun_turns.get(racer_id, 0) > 0:
            amount *= 0.1
        new_pos = max(0.0, self.positions[racer_id] + amount)
        self.positions[racer_id] = new_pos

    def apply_stun(self, racer_id, turns):
        self.stun_turns[racer_id] = max(self.stun_turns.get(racer_id, 0), turns)

    def tick_stun(self, racer_id):
        if self.stun_turns.get(racer_id, 0) > 0:
            self.stun_turns[racer_id] -= 1

    def check_finish(self, racer_id, current_turn):
        if self.finished_turn.get(racer_id) is None and self.positions[racer_id] >= self.tile_count:
            self.positions[racer_id] = self.tile_count
            self.finished_turn[racer_id] = current_turn

    def ranking(self):
        finished = [rid for rid in self.positions if self.finished_turn[rid] is not None]
        unfinished = [rid for rid in self.positions if self.finished_turn[rid] is None]
        finished.sort(key=lambda rid: self.finished_turn[rid])
        unfinished.sort(key=lambda rid: self.positions[rid], reverse=True)
        return finished + unfinished

    def distance_between(self, id_a, id_b):
        return abs(self.positions[id_a] - self.positions[id_b])

    def closest_rival(self, player_id, rival_ids):
        best_id = None
        best_dist = None
        for rid in rival_ids:
            if self.finished_turn.get(rid) is not None:
                continue
            d = self.distance_between(player_id, rid)
            if best_dist is None or d < best_dist:
                best_dist = d
                best_id = rid
        return best_id, best_dist

    def draw_minimap(self, x, y, w, h, colors):
        pyxel.rect(x, y, w, h, COL_GRAY)
        pyxel.line(x, y + h // 2, x + w, y + h // 2, COL_BLACK)
        pyxel.text(x + w - 16, y - 8, "GOAL", COL_WHITE)
        for racer_id, pos in self.positions.items():
            t = max(0.0, min(1.0, pos / self.tile_count))
            dx = x + w * t
            col = colors.get(racer_id, COL_WHITE)
            pyxel.circ(dx, y + h // 2, 3, col)
