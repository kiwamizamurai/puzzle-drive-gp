from PIL import Image

from mathart import flower_mandala

SUPERSAMPLE = 1024

big = flower_mandala(SUPERSAMPLE)

icon = big.resize((256, 256), Image.LANCZOS)
icon.save("icon.png")

favicon = big.resize((64, 64), Image.LANCZOS)
favicon.save("favicon.png")

print("wrote icon.png (256x256) and favicon.png (64x64)")
