import math

from PIL import Image, ImageDraw

ATTR_RGB = [
    (0xD4, 0x18, 0x6C),
    (0x39, 0x5C, 0x98),
    (0x70, 0xC6, 0xA9),
    (0xE9, 0xC3, 0x5B),
    (0x7E, 0x20, 0x72),
]

BG_RGB = (0x0F, 0x0F, 0x1E)
WHITE_RGB = (0xEE, 0xEE, 0xEE)


def petal_circle_center(cx, cy, radius, angle):
    return cx + radius * math.cos(angle), cy + radius * math.sin(angle)


def flower_petals(cx, cy, radius, n=5, rotation=-math.pi / 2):
    """5 circles of the classic r = sin(theta) petal shape, swept around a point."""
    petals = []
    for i in range(n):
        angle = rotation + 2 * math.pi * i / n
        pcx, pcy = petal_circle_center(cx, cy, radius / 2, angle)
        petals.append((pcx, pcy, radius / 2, angle))
    return petals


def square_wave_epicycle_points(cx, cy, scale, terms=4, steps=240, rotation=0.0):
    """Fourier series for a square wave, drawn as an epicycle path (classic
    'Fourier drawing' construction: sum of odd harmonics with 1/k amplitude)."""
    pts = []
    for i in range(steps + 1):
        t = 2 * math.pi * i / steps
        x, y = 0.0, 0.0
        for k in range(terms):
            n = 2 * k + 1
            amp = scale / n
            x += amp * math.cos(n * t + rotation)
            y += amp * math.sin(n * t + rotation)
        pts.append((cx + x, cy + y))
    return pts


def lissajous_points(cx, cy, a, b, delta, sx, sy, steps=720, t_max=2 * math.pi):
    pts = []
    for i in range(steps + 1):
        t = t_max * i / steps
        x = cx + sx * math.sin(a * t + delta)
        y = cy + sy * math.sin(b * t)
        pts.append((x, y))
    return pts


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def flower_mandala(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx, cy = size / 2, size / 2
    outer_r = size * 0.47

    backdrop = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bd_draw = ImageDraw.Draw(backdrop)
    bd_draw.ellipse(
        [cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r],
        fill=(*BG_RGB, 255),
    )
    img = Image.alpha_composite(img, backdrop)

    petal_r = size * 0.30
    for i, (pcx, pcy, pr, _angle) in enumerate(flower_petals(cx, cy, petal_r, n=5)):
        layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        col = ATTR_RGB[i % len(ATTR_RGB)]
        ld.ellipse([pcx - pr, pcy - pr, pcx + pr, pcy + pr], fill=(*col, 195))
        img = Image.alpha_composite(img, layer)

    curve_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cd = ImageDraw.Draw(curve_layer)
    pts = square_wave_epicycle_points(cx, cy, size * 0.10, terms=4, steps=240)
    cd.line(pts, fill=(*WHITE_RGB, 230), width=max(2, size // 220), joint="curve")
    img = Image.alpha_composite(img, curve_layer)

    border_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bord = ImageDraw.Draw(border_layer)
    bord.ellipse(
        [cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r],
        outline=(*WHITE_RGB, 255),
        width=max(2, size // 170),
    )
    img = Image.alpha_composite(img, border_layer)

    return img
