from pathlib import Path

from PIL import Image

from mathart import flower_mandala

SUPERSAMPLE = 1024
OUT_DIR = Path(__file__).resolve().parent.parent / "assets"

big = flower_mandala(SUPERSAMPLE)

icon = big.resize((256, 256), Image.LANCZOS)
icon.save(OUT_DIR / "icon.png")

favicon = big.resize((64, 64), Image.LANCZOS)
favicon.save(OUT_DIR / "favicon.png")

print(f"wrote {OUT_DIR / 'icon.png'} and {OUT_DIR / 'favicon.png'}")
