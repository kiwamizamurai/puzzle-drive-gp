import math
import random

import pyxel

import sound
import vecmath
from constants import (
    AIM_TURN_RATE,
    ARENA_H,
    ARENA_W,
    ARENA_X,
    ARENA_Y,
    COL_BLACK,
    COL_GRAY,
    COL_LIME,
    COL_RED,
    COL_WHITE,
    COL_YELLOW,
    COLLISION_RESTITUTION,
    DAMAGE_PER_SPEED,
    DUEL_MAX_ROUNDS,
    FRICTION,
    MAX_CHARGE_FRAMES,
    MAX_LAUNCH_SPEED,
    MAX_ROUND_FRAMES,
    SETTLE_SPEED,
    TOKEN_RADIUS,
    WALL_RESTITUTION,
)
from vecmath import clamp

PHASE_PLAYER_AIM = 0
PHASE_PLAYER_SIM = 1
PHASE_RIVAL_AIM = 2
PHASE_RIVAL_SIM = 3
PHASE_ROUND_END = 4
PHASE_DONE = 5

ROUND_END_FRAMES = 30


class DuelToken:
    def __init__(self, x, y, power_stat, hp, color):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.power_stat = power_stat
        self.hp = hp
        self.max_hp = hp
        self.color = color

    @property
    def mass(self):
        return 1.0 + self.power_stat * 0.05

    def speed(self):
        return math.hypot(self.vx, self.vy)

    def moving(self):
        return self.speed() > SETTLE_SPEED


def step_physics(tokens):
    min_x = ARENA_X + TOKEN_RADIUS
    max_x = ARENA_X + ARENA_W - TOKEN_RADIUS
    min_y = ARENA_Y + TOKEN_RADIUS
    max_y = ARENA_Y + ARENA_H - TOKEN_RADIUS

    for t in tokens:
        if not t.moving():
            t.vx = 0.0
            t.vy = 0.0
            continue
        t.x += t.vx
        t.y += t.vy
        t.vx *= FRICTION
        t.vy *= FRICTION

        bounced = False
        if t.x < min_x:
            t.x = min_x
            t.vx = -t.vx * WALL_RESTITUTION
            bounced = True
        elif t.x > max_x:
            t.x = max_x
            t.vx = -t.vx * WALL_RESTITUTION
            bounced = True
        if t.y < min_y:
            t.y = min_y
            t.vy = -t.vy * WALL_RESTITUTION
            bounced = True
        elif t.y > max_y:
            t.y = max_y
            t.vy = -t.vy * WALL_RESTITUTION
            bounced = True

        if bounced:
            sound.play_wall_bounce()

    return resolve_collisions(tokens)


def resolve_collisions(tokens):
    events = []
    n = len(tokens)
    min_dist = TOKEN_RADIUS * 2
    for i in range(n):
        for j in range(i + 1, n):
            a, b = tokens[i], tokens[j]
            dx = b.x - a.x
            dy = b.y - a.y
            dist = math.hypot(dx, dy)
            if dist >= min_dist or dist <= 0:
                continue
            nx, ny = dx / dist, dy / dist

            rel_vx = a.vx - b.vx
            rel_vy = a.vy - b.vy
            closing_speed = rel_vx * nx + rel_vy * ny

            if closing_speed > 0:
                speed_a = a.speed()
                speed_b = b.speed()
                if speed_a >= speed_b:
                    attacker, defender = a, b
                else:
                    attacker, defender = b, a
                damage = closing_speed * DAMAGE_PER_SPEED * (1.0 + attacker.power_stat * 0.02)
                defender.hp = max(0.0, defender.hp - damage)
                events.append((attacker, defender, damage))
                sound.play_duel_hit()

                inv_ma = 1.0 / a.mass
                inv_mb = 1.0 / b.mass
                j_impulse = -(1 + COLLISION_RESTITUTION) * closing_speed / (inv_ma + inv_mb)
                ix, iy = j_impulse * nx, j_impulse * ny
                a.vx += ix * inv_ma
                a.vy += iy * inv_ma
                b.vx -= ix * inv_mb
                b.vy -= iy * inv_mb

            overlap = min_dist - dist
            correction = overlap / 2 + 0.05
            a.x -= nx * correction
            a.y -= ny * correction
            b.x += nx * correction
            b.y += ny * correction

    return events


class DuelArena:
    def __init__(self, player_power, player_hp, rival_power, rival_hp):
        self.player = DuelToken(
            ARENA_X + 36, ARENA_Y + ARENA_H / 2, player_power, player_hp, COL_LIME
        )
        self.rival = DuelToken(
            ARENA_X + ARENA_W - 36, ARENA_Y + ARENA_H / 2, rival_power, rival_hp, COL_RED
        )
        self.round = 1
        self.phase = PHASE_PLAYER_AIM
        self.aim_angle = 0.0
        self.charge_frames = 0
        self.was_charging = False
        self.round_frames = 0
        self.round_end_timer = 0
        self.finished = False
        self.winner = None
        self.last_events = []

    def update(self, aim_dir, charging):
        if self.finished:
            return

        if self.phase == PHASE_PLAYER_AIM:
            if aim_dir != 0:
                self.aim_angle += aim_dir * AIM_TURN_RATE
            if charging:
                self.charge_frames = min(self.charge_frames + 1, MAX_CHARGE_FRAMES)
            released = self.was_charging and not charging
            self.was_charging = charging
            if released and self.charge_frames > 0:
                self._launch(self.player, self.aim_angle, self.charge_frames)
                self.charge_frames = 0
                self.round_frames = 0
                self.phase = PHASE_PLAYER_SIM

        elif self.phase == PHASE_PLAYER_SIM:
            self._sim_step()

        elif self.phase == PHASE_RIVAL_AIM:
            self._rival_launch()
            self.round_frames = 0
            self.phase = PHASE_RIVAL_SIM

        elif self.phase == PHASE_RIVAL_SIM:
            self._sim_step()

        elif self.phase == PHASE_ROUND_END:
            self.round_end_timer -= 1
            if self.round_end_timer <= 0:
                self._advance_round()

    def _launch(self, token, angle, charge_frames):
        power_fraction = clamp(charge_frames / MAX_CHARGE_FRAMES, 0.0, 1.0)
        speed = MAX_LAUNCH_SPEED * power_fraction
        token.vx = math.cos(angle) * speed
        token.vy = math.sin(angle) * speed
        sound.play_duel_launch()

    def _rival_launch(self):
        angle = vecmath.angle_to(self.rival.x, self.rival.y, self.player.x, self.player.y)
        angle += random.uniform(-0.3, 0.3)
        power_fraction = random.uniform(0.55, 1.0)
        self.rival.vx = math.cos(angle) * MAX_LAUNCH_SPEED * power_fraction
        self.rival.vy = math.sin(angle) * MAX_LAUNCH_SPEED * power_fraction
        sound.play_duel_launch()

    def _sim_step(self):
        events = step_physics([self.player, self.rival])
        if events:
            self.last_events.extend(events)
        self.round_frames += 1

        if self.player.hp <= 0 or self.rival.hp <= 0:
            self.finished = True
            self.winner = "rival" if self.player.hp <= 0 else "player"
            self.phase = PHASE_DONE
            return

        settled = not self.player.moving() and not self.rival.moving()
        if settled or self.round_frames >= MAX_ROUND_FRAMES:
            if self.phase == PHASE_PLAYER_SIM:
                self.phase = PHASE_RIVAL_AIM
            else:
                self.round_end_timer = ROUND_END_FRAMES
                self.phase = PHASE_ROUND_END

    def _advance_round(self):
        self.round += 1
        if self.round > DUEL_MAX_ROUNDS:
            self.finished = True
            self.winner = self._decide_winner_by_hp()
            self.phase = PHASE_DONE
        else:
            self.phase = PHASE_PLAYER_AIM

    def _decide_winner_by_hp(self):
        if self.rival.hp > self.player.hp:
            return "rival"
        return "player"

    def draw(self):
        pyxel.rect(ARENA_X, ARENA_Y, ARENA_W, ARENA_H, COL_BLACK)
        pyxel.rectb(ARENA_X, ARENA_Y, ARENA_W, ARENA_H, COL_WHITE)

        for token, label in ((self.player, "YOU"), (self.rival, "RIVAL")):
            pyxel.circ(token.x, token.y, TOKEN_RADIUS, token.color)
            pyxel.circb(token.x, token.y, TOKEN_RADIUS, COL_BLACK)
            bar_w = TOKEN_RADIUS * 2
            bar_x = token.x - TOKEN_RADIUS
            bar_y = token.y - TOKEN_RADIUS - 8
            pyxel.rect(bar_x, bar_y, bar_w, 3, COL_GRAY)
            hp_frac = max(0.0, token.hp / token.max_hp)
            pyxel.rect(bar_x, bar_y, int(bar_w * hp_frac), 3, COL_LIME)

        if self.phase == PHASE_PLAYER_AIM:
            aim_len = 14 + 10 * (self.charge_frames / MAX_CHARGE_FRAMES)
            ex = self.player.x + math.cos(self.aim_angle) * aim_len
            ey = self.player.y + math.sin(self.aim_angle) * aim_len
            pyxel.line(self.player.x, self.player.y, ex, ey, COL_YELLOW)
            pyxel.rect(ARENA_X, ARENA_Y + ARENA_H + 4, ARENA_W, 4, COL_GRAY)
            frac = self.charge_frames / MAX_CHARGE_FRAMES
            pyxel.rect(ARENA_X, ARENA_Y + ARENA_H + 4, int(ARENA_W * frac), 4, COL_RED)

        pyxel.text(ARENA_X, ARENA_Y - 10, f"ROUND {min(self.round, DUEL_MAX_ROUNDS)}/{DUEL_MAX_ROUNDS}", COL_WHITE)
