import math

import pyxel

SFX_CH = 2

PENTATONIC = [0, 2, 4, 7, 9]
NOTE_NAMES = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]


def _degree_to_note(index, base_octave):
    n = len(PENTATONIC)
    octave = base_octave + index // n
    offset = PENTATONIC[index % n]
    return f"{NOTE_NAMES[offset]}{octave}"


def _generate_melody_notes(steps=32):
    notes = []
    for t in range(steps):
        value = (
            1.6 * math.sin(2 * math.pi * t / 8)
            + 0.9 * math.sin(2 * math.pi * t / 3 + 0.4)
            + 0.5 * math.sin(2 * math.pi * t / 5 + 1.1)
        )
        norm = max(0.0, min(1.0, (value + 3.0) / 6.0))
        degree = int(round(norm * 8))
        notes.append(_degree_to_note(degree, base_octave=3))
    return "".join(notes)


def _generate_bass_notes(steps=32):
    notes = []
    for t in range(steps):
        degree = 0 if (t // 4) % 2 == 0 else 3
        notes.append(_degree_to_note(degree, base_octave=2))
    return "".join(notes)


def init_sounds():
    pyxel.sounds[0].set(notes="c3", tones="p", volumes="3", effects="n", speed=20)
    pyxel.sounds[1].set(notes="e3g3c4", tones="p", volumes="4", effects="n", speed=8)
    pyxel.sounds[2].set(notes="c3", tones="s", volumes="2", effects="n", speed=15)
    pyxel.sounds[3].set(notes="c3g3", tones="s", volumes="4", effects="n", speed=6)
    pyxel.sounds[4].set(notes="a2", tones="t", volumes="3", effects="n", speed=10)
    pyxel.sounds[5].set(notes="c2a1", tones="n", volumes="4", effects="f", speed=8)
    pyxel.sounds[6].set(notes="f2d2", tones="n", volumes="3", effects="f", speed=12)
    pyxel.sounds[7].set(
        notes="c3e3g3c4e4g4c4", tones="s", volumes="4", effects="n", speed=6
    )
    pyxel.sounds[8].set(notes="c3e3", tones="p", volumes="3", effects="n", speed=10)
    pyxel.sounds[9].set(
        notes="c3e3g3c4g4c4", tones="s", volumes="4", effects="n", speed=5
    )

    melody_notes = _generate_melody_notes(32)
    bass_notes = _generate_bass_notes(32)
    pyxel.sounds[20].set(notes=melody_notes, tones="t", volumes="2", effects="n", speed=20)
    pyxel.sounds[21].set(notes=bass_notes, tones="p", volumes="1", effects="n", speed=20)
    pyxel.musics[0].set([20], [21], [], [])


def play_menu():
    pyxel.play(SFX_CH, 0)


def play_match():
    pyxel.play(SFX_CH, 1)


def play_board_step():
    pyxel.play(SFX_CH, 2)


def play_duel_launch():
    pyxel.play(SFX_CH, 3)


def play_wall_bounce():
    pyxel.play(SFX_CH, 4)


def play_duel_hit():
    pyxel.play(SFX_CH, 5)


def play_stun():
    pyxel.play(SFX_CH, 6)


def play_victory():
    pyxel.play(SFX_CH, 7)


def play_gacha_pull():
    pyxel.play(SFX_CH, 8)


def play_rare_pull():
    pyxel.play(SFX_CH, 9)


def play_bgm():
    pyxel.playm(0, loop=True)


def stop_bgm():
    pyxel.stop(0)
    pyxel.stop(1)
