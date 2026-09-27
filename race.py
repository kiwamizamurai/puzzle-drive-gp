import pyxel

import sound
from board import Board
from constants import (
    ATTR_COLORS,
    CHARGE_MAX,
    COL_BLACK,
    COL_GRAY,
    COL_WHITE,
    COL_YELLOW,
    DUEL_COOLDOWN_TURNS,
    DUEL_LOSE_RETREAT,
    DUEL_TRIGGER_RANGE,
    DUEL_WIN_ADVANCE,
    HP_BASE,
    HP_PER_POWER,
    INTRO_FRAMES,
    MAX_TURNS,
    RACE_PHASE_BOARD,
    RACE_PHASE_DUEL,
    RACE_PHASE_FINISH,
    RACE_PHASE_INTRO,
    RACE_PHASE_PUZZLE,
    REFERENCE_SPEED,
    SCREEN_H,
    SCREEN_W,
    STUN_TURNS,
)
from driver import Driver
from duel import DuelArena
from puzzle import PuzzleGrid, compute_effects
from rival import Rival

BOARD_SHOW_FRAMES = 30
REWARD_TABLE = {1: 200, 2: 130, 3: 80, 4: 40}


class Race:
    def __init__(self, board_config, profile):
        self.profile = profile
        self.board = Board(board_config["tile_count"], board_config["name"], board_config["theme_col"])
        self.board.register(0)
        self.player_color = ATTR_COLORS[profile.leader().attribute]

        self.rivals = []
        for i, template_id in enumerate(board_config["rival_template_ids"]):
            racer_id = i + 1
            driver = Driver(template_id, level=board_config["rival_level"])
            rival = Rival(racer_id, driver, ATTR_COLORS[driver.attribute])
            self.rivals.append(rival)
            self.board.register(racer_id)

        self.turn = 1
        self.phase = RACE_PHASE_INTRO
        self.intro_timer = INTRO_FRAMES
        self.duel_cooldowns = {}
        self.puzzle = None
        self.duel = None
        self.duel_target_id = None
        self.pending_duel_id = None
        self.charge_meter = 0
        self.board_show_timer = 0
        self.last_turn_effects = None

        self.finished = False
        self.result_rank = None
        self.result_currency_gain = 0
        self.result_xp_gain = 0

    def update(self, move_col, move_row, hold, force_end, aim_dir, charging):
        if self.finished:
            return

        if self.phase == RACE_PHASE_INTRO:
            self.intro_timer -= 1
            if self.intro_timer <= 0:
                self._start_puzzle_phase()

        elif self.phase == RACE_PHASE_PUZZLE:
            self.puzzle.update(move_col, move_row, hold, force_end)
            if self.puzzle.resolved:
                self._apply_puzzle_result()

        elif self.phase == RACE_PHASE_BOARD:
            self.board_show_timer -= 1
            if self.board_show_timer <= 0:
                self._after_board_show()

        elif self.phase == RACE_PHASE_DUEL:
            self.duel.update(aim_dir, charging)
            if self.duel.finished:
                self._apply_duel_result()

    def _start_puzzle_phase(self):
        self.puzzle = PuzzleGrid()
        self.phase = RACE_PHASE_PUZZLE

    def _find_rival(self, racer_id):
        for r in self.rivals:
            if r.racer_id == racer_id:
                return r
        return None

    def _apply_puzzle_result(self):
        leader = self.profile.leader()
        speed, power, luck = self.profile.team_effective_stats()
        speed_mult = speed / REFERENCE_SPEED
        luck_mult = max(0.5, luck / REFERENCE_SPEED)
        effects = compute_effects(self.puzzle.matches_by_color, leader.attribute, speed_mult, luck_mult)
        self.last_turn_effects = effects

        self.board.advance(0, effects["advance"])
        self.profile.currency += effects["currency"]
        self.charge_meter = min(CHARGE_MAX, self.charge_meter + effects["charge"])

        for rival in self.rivals:
            self.board.advance(rival.racer_id, rival.simulated_advance())

        for racer_id in list(self.board.positions.keys()):
            self.board.tick_stun(racer_id)
            self.board.check_finish(racer_id, self.turn)

        for rid in list(self.duel_cooldowns.keys()):
            if self.duel_cooldowns[rid] > 0:
                self.duel_cooldowns[rid] -= 1

        self.pending_duel_id = None
        rival_ids = [r.racer_id for r in self.rivals]
        closest_id, dist = self.board.closest_rival(0, rival_ids)
        if (
            closest_id is not None
            and dist is not None
            and dist <= DUEL_TRIGGER_RANGE
            and self.duel_cooldowns.get(closest_id, 0) <= 0
        ):
            self.pending_duel_id = closest_id

        sound.play_board_step()
        self.phase = RACE_PHASE_BOARD
        self.board_show_timer = BOARD_SHOW_FRAMES

    def _after_board_show(self):
        if self.pending_duel_id is not None:
            self._start_duel(self.pending_duel_id)
        else:
            self._check_end_or_next_turn()

    def _start_duel(self, rival_id):
        rival = self._find_rival(rival_id)
        speed, power, luck = self.profile.team_effective_stats()
        player_hp = HP_BASE + power * HP_PER_POWER + self.charge_meter * 0.5
        rival_power = rival.driver.effective_power()
        rival_hp = HP_BASE + rival_power * HP_PER_POWER
        self.duel = DuelArena(power, player_hp, rival_power, rival_hp)
        self.duel_target_id = rival_id
        self.charge_meter = 0
        self.phase = RACE_PHASE_DUEL

    def _apply_duel_result(self):
        rival_id = self.duel_target_id
        if self.duel.winner == "player":
            self.board.advance(0, DUEL_WIN_ADVANCE)
            self.board.advance(rival_id, -DUEL_LOSE_RETREAT)
            self.board.apply_stun(rival_id, STUN_TURNS)
        else:
            self.board.advance(rival_id, DUEL_WIN_ADVANCE)
            self.board.advance(0, -DUEL_LOSE_RETREAT)
            self.board.apply_stun(0, STUN_TURNS)
        sound.play_stun()

        self.duel_cooldowns[rival_id] = DUEL_COOLDOWN_TURNS
        self.board.check_finish(0, self.turn)
        self.board.check_finish(rival_id, self.turn)
        self._check_end_or_next_turn()

    def _check_end_or_next_turn(self):
        if self.board.finished_turn.get(0) is not None or self.turn >= MAX_TURNS:
            self._finish_race()
        else:
            self.turn += 1
            self._start_puzzle_phase()

    def _finish_race(self):
        self.finished = True
        self.phase = RACE_PHASE_FINISH

        ranking = self.board.ranking()
        rank = ranking.index(0) + 1
        currency_gain = REWARD_TABLE.get(rank, 20)
        xp_gain = max(10, 60 - rank * 10)

        self.profile.currency += currency_gain
        leader = self.profile.leader()
        if leader is not None:
            leader.gain_xp(xp_gain)
        for sub in self.profile.subs():
            sub.gain_xp(xp_gain // 2)
        self.profile.races_completed += 1

        self.result_rank = rank
        self.result_currency_gain = currency_gain
        self.result_xp_gain = xp_gain
        sound.play_victory()

    def draw(self):
        pyxel.cls(COL_BLACK)
        pyxel.text(6, 4, f"{self.board.name}  TURN {min(self.turn, MAX_TURNS)}/{MAX_TURNS}", COL_WHITE)

        if self.phase != RACE_PHASE_DUEL:
            colors = {0: self.player_color}
            for r in self.rivals:
                colors[r.racer_id] = r.color
            self.board.draw_minimap(20, 24, SCREEN_W - 40, 16, colors)

            pyxel.text(6, 48, "DUEL", COL_WHITE)
            pyxel.rect(36, 48, 80, 6, COL_GRAY)
            frac = self.charge_meter / CHARGE_MAX
            pyxel.rect(36, 48, int(80 * frac), 6, COL_YELLOW)

        if self.phase == RACE_PHASE_INTRO:
            pyxel.text(SCREEN_W // 2 - 20, SCREEN_H // 2, f"TURN {self.turn}", COL_WHITE)
        elif self.phase == RACE_PHASE_PUZZLE:
            self.puzzle.draw()
        elif self.phase == RACE_PHASE_BOARD:
            if self.last_turn_effects:
                e = self.last_turn_effects
                pyxel.text(
                    6, 62, f"ADVANCE +{e['advance']:.1f}  COIN +{e['currency']:.0f}", COL_WHITE
                )
        elif self.phase == RACE_PHASE_DUEL:
            self.duel.draw()
