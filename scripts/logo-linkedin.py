# Logo cuadrado (400×400, fondo oscuro) para LinkedIn y perfiles: el original es blanco sobre transparente.
# uv run --with pillow python scripts/logo-linkedin.py media/logo-smagnet.png media/logo-linkedin-smagnet.png
import sys
from PIL import Image

src = Image.open(sys.argv[1]).convert('RGBA')
N = 400
bg = Image.new('RGBA', (N, N), (11, 11, 11, 255))
w, h = src.size
k = N * 0.84 / max(w, h)
logo = src.resize((round(w * k), round(h * k)), Image.LANCZOS)
bg.alpha_composite(logo, ((N - logo.width) // 2, (N - logo.height) // 2))
bg.convert('RGB').save(sys.argv[2])
