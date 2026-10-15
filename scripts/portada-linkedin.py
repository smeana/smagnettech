# Portada de la página de empresa de LinkedIn (1128×191 recomendado; se genera a 2x: 2256×382).
# Fondo: media/portada-fondo.png (ChatGPT, 2048×768, sin texto): se recorta la franja central, la que queda libre
# entre las dos ondas, y encima va el logo horizontal (media/logo-texto-maestro.png, sin fondo). LinkedIn recorta
# los lados (más aún en el móvil) y el logo de la página tapa la esquina inferior izquierda: el logo va algo a la
# derecha del centro, lejos de los bordes.
# uv run --with pillow python scripts/portada-linkedin.py media/portada-fondo.png media/logo-texto-maestro.png media/portada-linkedin-smagnet.png
import sys
from PIL import Image

W, H = 2256, 382
fondo = Image.open(sys.argv[1]).convert('RGB')
alto = round(H * fondo.width / W)
CENTRO = 374  # centro de la franja vacía en el fondo original
img = fondo.crop((0, CENTRO - alto // 2, fondo.width, CENTRO - alto // 2 + alto)).resize((W, H), Image.LANCZOS).convert('RGBA')

# Logo horizontal sin fondo (mismo tratamiento que scripts/logo.py).
maestro = Image.open(sys.argv[2]).convert('RGB')
logo = Image.new('RGBA', maestro.size)
logo.putdata([
    (0, 0, 0, 0) if (m := max(p)) <= 12 else
    (*(min(255, round(c * 255 / a)) for c in p), a) if (a := min(255, round((m - 12) * 255 / 228))) else (0, 0, 0, 0)
    for p in maestro.get_flattened_data()
])
logo = logo.crop(logo.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox())
ALTO_LOGO = 150
logo = logo.resize((round(logo.width * ALTO_LOGO / logo.height), ALTO_LOGO), Image.LANCZOS)
x = round(W * 0.78) - logo.width  # borde derecho al 78 %
img.alpha_composite(logo, (x, (H - ALTO_LOGO) // 2))
img.convert('RGB').save(sys.argv[3])
