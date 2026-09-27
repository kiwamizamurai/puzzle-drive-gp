import math


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distance_sq(x1, y1, x2, y2):
    return (x2 - x1) ** 2 + (y2 - y1) ** 2


def angle_to(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)


def normalize_angle(a):
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp(a, b, t):
    return a + (b - a) * t


def closest_point_on_segment(px, py, ax, ay, bx, by):
    abx = bx - ax
    aby = by - ay
    length_sq = abx * abx + aby * aby
    if length_sq == 0:
        return ax, ay, 0.0
    t = ((px - ax) * abx + (py - ay) * aby) / length_sq
    t = clamp(t, 0.0, 1.0)
    return ax + abx * t, ay + aby * t, t


def reflect(vx, vy, nx, ny):
    dot = vx * nx + vy * ny
    return vx - 2 * dot * nx, vy - 2 * dot * ny
