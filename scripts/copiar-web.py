#!/usr/bin/env python3
"""Copia estática de la web WordPress de smagnettech.com (alojamiento de OVH) en public/.

Descarga cada página y todo lo que usa (CSS, JS, imágenes, fuentes), cambia los enlaces
?page_id=N por rutas limpias y quita lo dinámico de WordPress (xmlrpc, feeds, API REST, oEmbed).
Uso: python3 scripts/copiar-web.py [IP del servidor de origen]
"""
import re
import shutil
import socket
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

DOMINIO = 'smagnettech.com'
ORIGEN = sys.argv[1] if len(sys.argv) > 1 else '213.32.37.233'
RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'public'

# ruta limpia -> consulta de WordPress
PAGINAS = {
    '/': '/',
    '/get-started/': '/?page_id=63',
    '/about-us/': '/?page_id=52',
    '/contact/': '/?page_id=42',
    '/privacy-policy/': '/?page_id=88',
    '/terms-and-conditions/': '/?page_id=95',
    '/cookies-policy/': '/?page_id=101',
}
RUTA_DE_ID = {q.split('=')[1]: r for r, q in PAGINAS.items() if '=' in q}

# El dominio ya no apunta a este servidor de forma fiable: se fuerza la IP de origen.
_resolver = socket.getaddrinfo
socket.getaddrinfo = lambda host, *a, **k: _resolver(ORIGEN if host == DOMINIO else host, *a, **k)
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE  # el certificado del origen no es válido


def bajar(ruta: str) -> bytes:
    req = urllib.request.Request(f'https://{DOMINIO}{ruta}', headers={'User-Agent': 'Mozilla/5.0 copia-estatica'})
    with urllib.request.urlopen(req, context=_ctx, timeout=60) as r:
        return r.read()


RE_URL_PROPIA = re.compile(r'(?:https?:)?(?:\\?/){2}' + re.escape(DOMINIO) + r'((?:\\?/)[^"\'\s<>)]*)?')
recursos: set[str] = set()


def ruta_recurso(url_path: str) -> str:
    """'/wp-content/x.css?ver=1' -> '/wp-content/x.css'."""
    return urllib.parse.unquote(url_path.split('?')[0].split('#')[0])


def reescribir(texto: str) -> str:
    def cambio(m: re.Match) -> str:
        escapado = '\\/' in m.group(0)
        ruta = (m.group(1) or '/').replace('\\/', '/')
        limpio = ruta.split('#')[0]
        ancla = ruta[len(limpio):]
        if limpio.startswith(('/wp-content/', '/wp-includes/')):
            recursos.add(ruta_recurso(limpio))
            nueva = ruta_recurso(limpio)
        else:
            q = urllib.parse.urlparse(limpio)
            ids = urllib.parse.parse_qs(q.query).get('page_id')
            if ids and ids[0] in RUTA_DE_ID:
                nueva = RUTA_DE_ID[ids[0]]
            elif q.path in ('', '/') and not q.query:
                nueva = '/'
            else:
                nueva = limpio  # se deja tal cual (se quitan aparte si es de WordPress)
        nueva += ancla
        return nueva.replace('/', '\\/') if escapado else nueva

    return RE_URL_PROPIA.sub(cambio, texto)


def limpiar_html(html: str) -> str:
    # Cabecera de WordPress que no sirve en una web estática.
    html = re.sub(r'<link[^>]+rel=["\'](?:EditURI|pingback|shortlink|https://api\.w\.org/|wlwmanifest)["\'][^>]*>\s*', '', html)
    html = re.sub(r'<link[^>]+(?:type=["\']application/(?:rss\+xml|json\+oembed|json|xml\+oembed|text/xml\+oembed)["\'])[^>]*>\s*', '', html)
    html = re.sub(r'<link[^>]+href=["\'][^"\']*(?:rest_route|xmlrpc\.php|feed=)[^"\']*["\'][^>]*>\s*', '', html)
    html = re.sub(r'<meta name=["\']generator["\'][^>]*>\s*', '', html)
    html = re.sub(r'<script[^>]*wp-emoji[^>]*>[\s\S]*?</script>\s*', '', html)
    html = re.sub(r'<script[^>]*>\s*window\._wpemojiSettings[\s\S]*?</script>\s*', '', html)
    html = reescribir(html)
    # Recursos pedidos por http:// en el original: ya son rutas relativas tras reescribir.
    return html


def css_recursos(ruta_css: str, css: str) -> str:
    base = ruta_css.rsplit('/', 1)[0] + '/'

    def cambio(m: re.Match) -> str:
        url = m.group(2).strip()
        if url.startswith(('data:', 'http://fonts', 'https://fonts', '#')):
            return m.group(0)
        if DOMINIO in url:
            url = re.sub(r'^(?:https?:)?//' + re.escape(DOMINIO), '', url)
        elif url.startswith(('http://', 'https://', '//')):
            return m.group(0)
        absoluta = urllib.parse.urljoin(base, url)
        recursos.add(ruta_recurso(absoluta))
        sufijo = '#' + url.split('#', 1)[1] if '#' in url else ''
        return f'url({m.group(1)}{ruta_recurso(absoluta)}{sufijo}{m.group(1)})'

    return re.sub(r'url\((["\']?)([^)"\']+)\1\)', cambio, css)


def main() -> None:
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir(parents=True)
    for ruta, consulta in PAGINAS.items():
        html = limpiar_html(bajar(consulta).decode('utf-8'))
        destino = SALIDA / ruta.strip('/') / 'index.html' if ruta != '/' else SALIDA / 'index.html'
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(html, encoding='utf-8')
        print('página', ruta)

    hechos: set[str] = set()
    fallos = []
    while recursos - hechos:
        ruta = sorted(recursos - hechos)[0]
        hechos.add(ruta)
        try:
            datos = bajar(urllib.parse.quote(ruta))
        except Exception as e:  # noqa: BLE001
            fallos.append(f'{ruta}: {e}')
            continue
        if ruta.endswith('.css'):
            datos = css_recursos(ruta, reescribir(datos.decode('utf-8'))).encode('utf-8')
        elif ruta.endswith('.js'):
            datos = reescribir(datos.decode('utf-8')).encode('utf-8')
        destino = SALIDA / ruta.lstrip('/')
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(datos)
    print(f'{len(hechos) - len(fallos)} recursos descargados')
    for f in fallos:
        print('FALLO', f)


if __name__ == '__main__':
    main()
