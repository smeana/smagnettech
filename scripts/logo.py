# Genera todas las versiones del logo a partir del maestro (símbolo blanco y verde sobre negro, 1254 px, ChatGPT 2026-10-15):
#   media/logo-smagnet.png            1024 px, fondo transparente (original para otros usos)
#   media/logo-linkedin-smagnet.png   400 px, fondo oscuro (LinkedIn y perfiles)
#   src/img/logo-96.png               cabecera y pie de la web (transparente)
#   src/img/icon-32.png, icon-180.png, favicon.ico, og.png   iconos (fondo oscuro: en pestañas claras el blanco se pierde)
#   src/firma/logo-firma-smagnet.png  firma de Gmail: solo se cambia el símbolo (mismo nombre y tamaño, ver CLAUDE.md)
# uv run --with pillow python scripts/logo.py media/logo-smagnet-maestro.png
import sys
from pathlib import Path
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
FONDO = (11, 13, 12)

maestro = Image.open(sys.argv[1]).convert('RGB')
# Recorte cuadrado ajustado al círculo (centro y diámetro medidos en el maestro).
CX, CY, R = 626, 621, 415
maestro = maestro.crop((CX - R, CY - R, CX + R, CY + R))

# Negro → transparente: alfa según el canal más claro; se despremultiplica para no dejar halo oscuro.
transparente = Image.new('RGBA', maestro.size)
px = [
    (0, 0, 0, 0) if (m := max(p)) <= 12 else
    (*(min(255, round(c * 255 / a)) for c in p), a) if (a := min(255, round((m - 12) * 255 / 228))) else (0, 0, 0, 0)
    for p in maestro.get_flattened_data()
]
transparente.putdata(px)


def simbolo(n: int, relleno: float = 1.0) -> Image.Image:
    """Símbolo transparente de n px que ocupa la fracción «relleno» del lienzo."""
    lado = round(n * relleno)
    s = transparente.resize((lado, lado), Image.LANCZOS)
    lienzo = Image.new('RGBA', (n, n))
    lienzo.alpha_composite(s, ((n - lado) // 2, (n - lado) // 2))
    return lienzo


def sobre_fondo(n: int, relleno: float) -> Image.Image:
    img = Image.new('RGBA', (n, n), (*FONDO, 255))
    img.alpha_composite(simbolo(n, relleno))
    return img.convert('RGB')


simbolo(1024, 0.94).save(RAIZ / 'media/logo-smagnet.png')
sobre_fondo(400, 0.8).save(RAIZ / 'media/logo-linkedin-smagnet.png')
simbolo(96).save(RAIZ / 'src/img/logo-96.png', optimize=True)
sobre_fondo(32, 0.9).save(RAIZ / 'src/img/icon-32.png', optimize=True)
sobre_fondo(180, 0.8).save(RAIZ / 'src/img/icon-180.png', optimize=True)
sobre_fondo(512, 0.7).save(RAIZ / 'src/img/og.png', optimize=True)
sobre_fondo(48, 0.9).save(RAIZ / 'src/img/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])

# Firma: el símbolo viejo ocupa x 23-117, y 16-109 sobre fondo negro (446×128, esquinas redondeadas transparentes).
firma_ruta = RAIZ / 'src/firma/logo-firma-smagnet.png'
firma = Image.open(firma_ruta).convert('RGBA')
ImageDraw.Draw(firma).rectangle([18, 10, 124, 118], fill=(0, 0, 0, 255))
firma.alpha_composite(simbolo(96), (22, 15))
firma.save(firma_ruta, optimize=True)
