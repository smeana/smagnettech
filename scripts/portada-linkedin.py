# Portada de la página de empresa de LinkedIn (1128×191 recomendado; se genera a 2x: 2256×382).
# Fondo: media/portada-fondo.png (ChatGPT, 2048×768, sin texto): se recorta la franja central, la que queda libre
# entre las dos ondas, y encima va el logo horizontal (media/logo-texto-maestro.png, sin fondo). LinkedIn recorta
# los lados (más aún en el móvil) y el logo de la página tapa la esquina inferior izquierda: el logo va algo a la
# derecha del centro, lejos de los bordes. Debajo, el lema y los servicios con las fuentes de la web (Exo 2 y Lato,
# OFL, en media/fuentes/).
# uv run --with pillow python scripts/portada-linkedin.py media/portada-fondo.png media/logo-texto-maestro.png media/portada-linkedin-smagnet.png
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

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
ALTO_LOGO = 92
logo = logo.resize((round(logo.width * ALTO_LOGO / logo.height), ALTO_LOGO), Image.LANCZOS)

FUENTES = Path(__file__).resolve().parent.parent / 'media/fuentes'
lema = ImageFont.truetype(FUENTES / 'Exo2.ttf', 58)
lema.set_variation_by_name('SemiBold')
servicios = ImageFont.truetype(FUENTES / 'Lato-Regular.ttf', 31)
LEMA = 'Software, data & AI that ship to production'
SERVICIOS = 'Architecture  ·  Data engineering  ·  AI  ·  Amazon Ads  ·  Cloud  ·  Fintech'

# Bloque centrado en el 56 % del ancho: fuera de la esquina del logo de la página y de los lados que recorta el móvil.
CX = round(W * 0.56)
img.alpha_composite(logo, (CX - logo.width // 2, 58))
d = ImageDraw.Draw(img)
d.text((CX, 238), LEMA, font=lema, fill=(255, 255, 255), anchor='ms')
d.text((CX, 298), SERVICIOS, font=servicios, fill=(163, 171, 166), anchor='ms')
img.convert('RGB').save(sys.argv[3])
