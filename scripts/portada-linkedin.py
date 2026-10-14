# Portada de la página de empresa de LinkedIn (1128×191 recomendado; se genera a 2x: 2256×382).
# El logo de la página tapa la esquina inferior izquierda, así que el texto va a la derecha.
# uv run --with pillow python scripts/portada-linkedin.py media/portada-linkedin-smagnet.png
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 2256, 382
img = Image.new('RGB', (W, H), (11, 13, 12))
d = ImageDraw.Draw(img)

# Rejilla tenue de líneas horizontales (como el logo) que se desvanece hacia la izquierda.
for y in range(0, H, 14):
    for x0 in range(0, W, 8):
        a = x0 / W
        c = round(11 + 22 * a)
        d.line([(x0, y), (x0 + 7, y)], fill=(c, c + 2, c + 1), width=2)

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
xd = W - 120
d.text((xd, 150), titulo, font=ft, fill=(255, 255, 255), anchor='rs')
d.text((xd, 240), sub, font=fs, fill=(163, 171, 166), anchor='rs')
d.rectangle([xd - 220, 280, xd, 288], fill=(12, 245, 126))
img.save(sys.argv[1])
