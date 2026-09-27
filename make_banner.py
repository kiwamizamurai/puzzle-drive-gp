from PIL import Image, ImageDraw, ImageFont

from mathart import ATTR_RGB, BG_RGB, WHITE_RGB, flower_mandala, lissajous_points

W, H = 1200, 400
SUPERSAMPLE = 2

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

LISSAJOUS_PARAMS = [
    (3, 2, 0.0),
    (3, 4, 1.5708),
    (5, 4, 0.7854),
    (5, 6, 0.0),
    (7, 6, 1.0472),
]


def render():
    w, h = W * SUPERSAMPLE, H * SUPERSAMPLE
    img = Image.new("RGBA", (w, h), (*BG_RGB, 255))

    wave_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wave_layer)
    cx, cy = w * 0.62, h * 0.5
    sx, sy = w * 0.46, h * 0.38
    for i, (a, b, delta) in enumerate(LISSAJOUS_PARAMS):
        pts = lissajous_points(cx, cy, a, b, delta, sx, sy, steps=1400)
        col = ATTR_RGB[i % len(ATTR_RGB)]
        wd.line(pts, fill=(*col, 90), width=max(2, w // 500), joint="curve")
    img = Image.alpha_composite(img, wave_layer)

    logo_size = int(h * 0.72)
    logo = flower_mandala(logo_size)
    img = img.convert("RGBA")
    img.alpha_composite(logo, (int(w * 0.05), int((h - logo_size) / 2)))

    draw = ImageDraw.Draw(img)
    title_font = ImageFont.truetype(FONT_BOLD, int(h * 0.16))
    sub_font = ImageFont.truetype(FONT_REGULAR, int(h * 0.06))

    title_x = int(w * 0.40)
    title_y = int(h * 0.34)
    draw.text((title_x + w * 0.004, title_y + h * 0.004), "PUZZLE DRIVE GP", font=title_font, fill=(0, 0, 0, 160))
    draw.text((title_x, title_y), "PUZZLE DRIVE GP", font=title_font, fill=(*WHITE_RGB, 255))

    sub_y = title_y + int(h * 0.22)
    draw.text((title_x, sub_y), "MATCH.  FLICK.  COLLECT.", font=sub_font, fill=(*ATTR_RGB[2], 255))

    border = ImageDraw.Draw(img)
    border.rectangle([0, 0, w - 1, h - 1], outline=(*WHITE_RGB, 60), width=max(1, w // 800))

    return img.resize((W, H), Image.LANCZOS).convert("RGB")


banner = render()
banner.save("banner.png")
print("wrote banner.png", banner.size)
