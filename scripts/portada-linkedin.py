# Portada de la página de empresa de LinkedIn (1128×191 recomendado; se genera a 2x: 2256×382).
# Fondo: media/portada-fondo.png (ChatGPT, 2048×768, sin texto); se recorta la franja central, la que queda libre
# entre las dos ondas, y el texto va ahí a la derecha (el logo de la página tapa la esquina inferior izquierda).
# uv run --with pillow python scripts/portada-linkedin.py media/portada-fondo.png media/portada-linkedin-smagnet.png
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 2256, 382
fondo = Image.open(sys.argv[1]).convert('RGB')
k = W / fondo.width
alto = round(H / k)
CENTRO = 374  # centro de la franja vacía en el fondo original
img = fondo.crop((0, CENTRO - alto // 2, fondo.width, CENTRO - alto // 2 + alto)).resize((W, H), Image.LANCZOS)
d = ImageDraw.Draw(img)


def fuente(tam: int, negrita: bool):
    for f in (['/System/Library/Fonts/Supplemental/Arial Bold.ttf'] if negrita else
              ['/System/Library/Fonts/Supplemental/Arial.ttf']):
        try:
            return ImageFont.truetype(f, tam)
        except OSError:
            pass
    return ImageFont.load_default(tam)


titulo = 'Software · Data · AI · Amazon Ads · Cloud · Fintech'
sub = 'Engineering that ships to production  —  smagnettech.com'
ft, fs = fuente(64, True), fuente(40, False)
xd = W - 160  # lejos del borde: en el móvil LinkedIn recorta los lados
d.text((xd, 172), titulo, font=ft, fill=(255, 255, 255), anchor='rs')
d.text((xd, 240), sub, font=fs, fill=(163, 171, 166), anchor='rs')
img.save(sys.argv[2])
