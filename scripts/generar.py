#!/usr/bin/env python3
"""Genera la web estática de smagnettech.com en public/ (HTML + CSS, sin WordPress).

Contenido: servicios del CV del titular (software architecture, data engineering, AI, Amazon Ads,
cloud/DevOps, fintech). Textos legales e imágenes: los de la web WordPress original, guardada en
original/ por scripts/copiar-web.py.
Uso: python3 scripts/generar.py
"""
import html
import re
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGINAL = RAIZ / 'original'
SALIDA = RAIZ / 'public'
SUBIDAS = ORIGINAL / 'wp-content/uploads/2024/09'
EMAIL = 'info@smagnettech.com'
URL = 'https://smagnettech.com'

NAV = [('/', 'Home'), ('/services/', 'Services'), ('/about-us/', 'About'), ('/get-started/', 'Get Started'), ('/contact/', 'Contact')]

# Iconos de trazo (24x24) en línea: nítidos y sin peticiones extra.
ICONOS = {
    'arquitectura': '<path d="M3 21h18M5 21V8l7-5 7 5v13M9 21v-6h6v6M9 11h.01M15 11h.01"/>',
    'datos': '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
    'ia': '<rect x="5" y="5" width="14" height="14" rx="2"/><path d="M9 9h6v6H9zM9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>',
    'amazon': '<path d="M3 3h2l2.4 11.2a2 2 0 0 0 2 1.6h7.7a2 2 0 0 0 2-1.5L21 7H6"/><circle cx="10" cy="20" r="1.5"/><circle cx="17" cy="20" r="1.5"/>',
    'nube': '<path d="M7 18a5 5 0 1 1 .9-9.9A6 6 0 0 1 19.5 10 4 4 0 0 1 18 18z"/><path d="M12 12v6M9.5 14.5 12 12l2.5 2.5"/>',
    'fintech': '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-7"/><path d="M16 7h4v4"/>',
}

SERVICIOS = [
    {
        'id': 'software-architecture', 'icono': 'arquitectura', 'titulo': 'Software Architecture & Engineering',
        'resumen': 'Scalable, low-latency systems designed end to end, from architecture to production support.',
        'puntos': ['System & solution architecture', 'Microservices and event-driven design (Kafka)',
                   'Low-latency services in Python, Rust, Java and C++', 'REST and gRPC APIs, legacy integration'],
        'detalle': 'We design and build production-grade software across the full lifecycle: architecture, '
                   'implementation, testing, deployment and support. Our background includes payment platforms, '
                   'real-time pricing engines and trading systems where latency, reliability and observability '
                   'are non-negotiable.',
    },
    {
        'id': 'data-engineering', 'icono': 'datos', 'titulo': 'Data Engineering',
        'resumen': 'Batch and streaming pipelines that turn raw data into reliable, analytics-ready assets.',
        'puntos': ['Streaming with Kafka and Confluent Cloud', 'Spark, Airflow and Delta Lake pipelines',
                   'Snowflake, BigQuery and Redshift warehouses', 'Data quality, monitoring and cloud migrations'],
        'detalle': 'From real-time ingestion to the data warehouse: we build pipelines with Spark, Kafka and Airflow, '
                   'set up data-quality controls and observability, and migrate legacy platforms to the cloud '
                   '(including a 120 TB migration to Google Cloud).',
    },
    {
        'id': 'ai-services', 'icono': 'ia', 'titulo': 'AI & Machine Learning',
        'resumen': 'Practical AI that automates work and improves decisions: LLMs, agents and predictive models.',
        'puntos': ['LLM applications and AI agents', 'AI-powered process automation',
                   'Forecasting and predictive models (incl. neural networks)', 'NLP and AI content generation'],
        'detalle': 'We integrate large language models into real workflows (content generation, classification, '
                   'assistants and agents) and build machine-learning models for forecasting and risk, always '
                   'measured against business metrics, not demos.',
    },
    {
        'id': 'amazon-ads', 'icono': 'amazon', 'titulo': 'Amazon Ads & Marketplace Automation',
        'resumen': 'Programmatic Amazon advertising and seller automation across global marketplaces.',
        'puntos': ['Sponsored Products, Brands, Display and TV via the Ads API',
                   'Algorithmic bid optimization with ACOS control', 'SP-API automation: stock, forecasting and reorders',
                   'Listing monitoring and LLM-powered listing SEO'],
        'detalle': 'We run the full advertising and analytics stack for Amazon sellers across 11 marketplaces '
                   '(US, UK, DE, ES, FR, IT, NL, PL, SE, BE, IE): automated campaign creation, keyword generation, '
                   'bid optimization, real-time P&amp;L dashboards, stock control with demand forecasting, and alerts '
                   'when Amazon changes your listings.',
    },
    {
        'id': 'cloud-devops', 'icono': 'nube', 'titulo': 'Cloud & DevOps',
        'resumen': 'Infrastructure as code, Kubernetes and CI/CD on AWS, Google Cloud and Azure.',
        'puntos': ['AWS, Google Cloud and Azure', 'Terraform and infrastructure as code',
                   'Docker, Kubernetes and serverless', 'CI/CD and GitOps with Argo CD'],
        'detalle': 'We automate infrastructure with Terraform, run containerized workloads on Kubernetes, Fargate and '
                   'serverless platforms, and ship with CI/CD and GitOps (Argo CD, Argo Workflows) for frequent, '
                   'reliable releases at a controlled cost.',
    },
    {
        'id': 'fintech', 'icono': 'fintech', 'titulo': 'Fintech & Quantitative Development',
        'resumen': 'Real-time market data, pricing and trading systems for banks, funds and crypto platforms.',
        'puntos': ['Real-time pricing and valuation (e.g. ETF iNAV)', 'Market data: Refinitiv, Bloomberg, CME',
                   'Pricing libraries for fixed income and rates', 'Crypto market making and exchange integration'],
        'detalle': 'Our quantitative work covers real-time ETF valuation pipelines, pricing libraries for swaps and '
                   'fixed income rewritten in Rust, market-data connectors, and low-latency arbitrage and '
                   'market-making systems connected to 30+ crypto exchanges.',
    },
]

CIFRAS = [('12+', 'years building production systems'), ('11', 'Amazon marketplaces automated'),
          ('30+', 'crypto exchanges integrated'), ('120 TB', 'migrated to the cloud')]

SECTORES = ['Investment banking', 'Payments', 'Asset management &amp; ETFs', 'Crypto exchanges',
            'E-commerce &amp; Amazon sellers', 'Automotive', 'Public sector (EU)']

STACK = ['Python', 'Rust', 'Java', 'C++', 'SQL', 'Kafka', 'Spark', 'Airflow', 'Snowflake', 'BigQuery', 'Delta Lake',
         'AWS', 'Google Cloud', 'Azure', 'Terraform', 'Kubernetes', 'Argo CD', 'Docker', 'OpenAI', 'Amazon Ads API',
         'Amazon SP-API', 'Grafana']

PASOS = [
    ('Tell us about your needs', 'Send us a short description of your project, goals and the challenges you are facing.'),
    ('Free consultation', 'We schedule a call to understand your context and explore the best technical approach.'),
    ('Customized plan', 'You receive a proposal with scope, architecture, timeline and cost.'),
    ('Delivery', 'We build in short iterations with continuous feedback, and support the solution in production.'),
]


def icono(nombre: str) -> str:
    return (f'<svg class="icono" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONOS[nombre]}</svg>')


def pagina(ruta: str, titulo: str, descripcion: str, cuerpo: str) -> None:
    nav = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if h == ruta else ""}>{t}</a>' for h, t in NAV)
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{descripcion}">
<link rel="canonical" href="{URL}{ruta}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descripcion}">
<meta property="og:url" content="{URL}{ruta}">
<meta property="og:image" content="{URL}/assets/og.png">
<meta name="theme-color" content="#000000">
<link rel="icon" href="/assets/icon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Exo+2:wght@400;500;600;700&family=Lato:wght@400;700&display=swap">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<header class="cabecera">
  <div class="contenedor cabecera__fila">
    <a class="logo" href="/" aria-label="Smagnet home"><img src="/assets/logo.png" alt="Smagnet" width="44" height="42"></a>
    <input type="checkbox" id="menu" class="menu__check" aria-label="Open menu">
    <label for="menu" class="menu__boton" aria-hidden="true"><span></span></label>
    <nav class="menu">{nav}</nav>
  </div>
</header>
<main>
{cuerpo}
</main>
<footer class="pie">
  <div class="contenedor pie__fila">
    <div>
      <img src="/assets/logo.png" alt="" width="40" height="38">
      <p><strong>SMAGNET LLC</strong><br>EIN: 61-2193900<br>407 Lincoln Road, Suite 12N<br>Miami Beach, FL 33139</p>
    </div>
    <div>
      <h4>Services</h4>
      {''.join(f'<a href="/services/#{s["id"]}">{s["titulo"]}</a>' for s in SERVICIOS)}
    </div>
    <div>
      <h4>Get in touch</h4>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
      <a href="/get-started/">Free consultation</a>
    </div>
    <div>
      <h4>Legal</h4>
      <a href="/privacy-policy/">Privacy Policy</a>
      <a href="/terms-and-conditions/">Terms and Conditions</a>
      <a href="/cookies-policy/">Cookies Policy</a>
    </div>
  </div>
  <p class="contenedor pie__copy">© 2026 Smagnet LLC. All rights reserved.</p>
</footer>
</body>
</html>
'''
    destino = SALIDA / ruta.strip('/') / 'index.html' if ruta != '/' else SALIDA / 'index.html'
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(doc, encoding='utf-8')


def cta() -> str:
    return f'''<section class="cta">
  <div class="contenedor">
    <h2>Let’s build the future together</h2>
    <p>Tell us what you need and we will set up a free consultation.</p>
    <a class="boton" href="mailto:{EMAIL}?subject=Free%20consultation">Set up a free consultation</a>
  </div>
</section>'''


def tarjetas() -> str:
    return ''.join(f'''<article class="tarjeta">
      {icono(s["icono"])}
      <h3><a href="/services/#{s["id"]}">{s["titulo"]}</a></h3>
      <p>{s["resumen"]}</p>
      <ul>{''.join(f"<li>{p}</li>" for p in s["puntos"])}</ul>
    </article>''' for s in SERVICIOS)


def inicio() -> None:
    cifras = ''.join(f'<div><strong>{n}</strong><span>{t}</span></div>' for n, t in CIFRAS)
    sectores = ''.join(f'<li>{s}</li>' for s in SECTORES)
    pasos = ''.join(f'<li><h3>{t}</h3><p>{d}</p></li>' for t, d in PASOS)
    pagina('/', 'Smagnet | Software Architecture, Data Engineering, AI & Amazon Ads',
           'Smagnet LLC builds software architecture, data engineering, AI and Amazon Ads automation solutions for '
           'businesses in finance, e-commerce and beyond.', f'''
<section class="heroe">
  <div class="contenedor heroe__fila">
    <div>
      <p class="antetitulo">Tailored software solutions</p>
      <h1>Software architecture, data engineering &amp; AI that ship to production</h1>
      <p class="entradilla">We design, build and run the systems behind your business: scalable software, real-time data
      pipelines, AI automation and Amazon advertising at scale.</p>
      <div class="botones">
        <a class="boton" href="/get-started/">Get started</a>
        <a class="boton boton--borde" href="/services/">Our services</a>
      </div>
    </div>
    <img class="heroe__img" src="/assets/heroe.png" alt="" width="490" height="490">
  </div>
</section>
<section class="cifras"><div class="contenedor cifras__fila">{cifras}</div></section>
<section class="seccion">
  <div class="contenedor">
    <h2>What we do</h2>
    <div class="rejilla">{tarjetas()}</div>
  </div>
</section>
<section class="seccion seccion--gris">
  <div class="contenedor dos">
    <div>
      <h2>Experience where it matters</h2>
      <p>Our team has spent more than a decade delivering production systems for global banks, crypto exchanges,
      asset managers, e-commerce brands, automotive and EU institutions, where reliability, latency and data quality
      are critical.</p>
      <a class="enlace" href="/about-us/">About us →</a>
    </div>
    <ul class="etiquetas">{sectores}</ul>
  </div>
</section>
<section class="seccion">
  <div class="contenedor">
    <h2>How we work</h2>
    <ol class="pasos">{pasos}</ol>
  </div>
</section>
{cta()}''')


def servicios() -> None:
    bloques = ''.join(f'''<article class="servicio" id="{s["id"]}">
      <div class="servicio__cab">{icono(s["icono"])}<h2>{s["titulo"]}</h2></div>
      <p>{s["detalle"]}</p>
      <ul>{''.join(f"<li>{p}</li>" for p in s["puntos"])}</ul>
    </article>''' for s in SERVICIOS)
    stack = ''.join(f'<li>{t}</li>' for t in STACK)
    pagina('/services/', 'Services | Smagnet',
           'Software architecture, data engineering, AI & machine learning, Amazon Ads automation, cloud & DevOps and '
           'fintech development.', f'''
<section class="cabecera-pagina"><div class="contenedor">
  <p class="antetitulo">Services</p>
  <h1>End-to-end technology services</h1>
  <p class="entradilla">From the first architecture diagram to production monitoring.</p>
</div></section>
<section class="seccion"><div class="contenedor servicios">{bloques}</div></section>
<section class="seccion seccion--gris"><div class="contenedor">
  <h2>Technology stack</h2>
  <ul class="etiquetas">{stack}</ul>
</div></section>
{cta()}''')


def sobre() -> None:
    pagina('/about-us/', 'About Us | Smagnet',
           'Smagnet LLC is a software, data and AI company with more than 12 years of experience in banking, '
           'trading, e-commerce and the public sector.', f'''
<section class="cabecera-pagina"><div class="contenedor">
  <p class="antetitulo">About Smagnet</p>
  <h1>Engineering-led, results-driven</h1>
  <p class="entradilla">Smagnet LLC delivers software engineering, data engineering and AI services that streamline
  operations and turn data into decisions.</p>
</div></section>
<section class="seccion"><div class="contenedor dos">
  <div>
    <h2>Our experience</h2>
    <p>Smagnet was founded by Sergio Meana, an electronic engineer specialized in software with more than 12 years
    building production systems as an architect, data engineer and quantitative developer.</p>
    <p>His work includes payment platforms and Kafka architectures for HSBC, pricing libraries and data platforms for
    Santander, real-time ETF valuation for Tradeweb (LSEG), machine-learning risk models for JP Morgan, a 120 TB cloud
    migration and forecasting for Jaguar Land Rover, Azure data architecture for the EUIPO, Spark pipelines for
    Adevinta, and low-latency market making for the crypto exchange Bit2Me. Since 2023 he has led Amazon advertising
    and marketplace automation for brands selling in 11 countries.</p>
  </div>
  <div class="caja">
    <h3>Certifications</h3>
    <ul><li>Google Cloud Certified Data Engineer</li><li>Microsoft Azure Fundamentals (AZ-900)</li>
    <li>Microsoft Azure Data Fundamentals (DP-900)</li></ul>
    <h3>Languages</h3>
    <ul><li>English</li><li>Spanish</li></ul>
  </div>
</div></section>
<section class="seccion seccion--gris"><div class="contenedor tres">
  <div><h3>Mission</h3><p>Empower businesses with software, data engineering and AI that streamline operations,
  improve decision-making and unlock new opportunities for growth.</p></div>
  <div><h3>Vision</h3><p>Be the technology partner companies trust to solve complex problems with systems that are
  reliable, efficient and built to last.</p></div>
  <div><h3>Why choose us</h3><p>Every business is different. We take a client-centric approach, tailoring each solution
  to your goals, with senior engineering on every project.</p></div>
</div></section>
{cta()}''')


def empezar() -> None:
    pasos = ''.join(f'<li><h3>{t}</h3><p>{d}</p></li>' for t, d in PASOS)
    pagina('/get-started/', 'Get Started | Smagnet',
           'Start your project with Smagnet: free consultation, customized plan and agile delivery.', f'''
<section class="cabecera-pagina"><div class="contenedor">
  <p class="antetitulo">Get started</p>
  <h1>Start your project with Smagnet</h1>
  <p class="entradilla">Ready to transform your business with software, data engineering, AI or Amazon Ads automation?
  Here is how we work.</p>
</div></section>
<section class="seccion"><div class="contenedor"><ol class="pasos">{pasos}</ol></div></section>
{cta()}''')


def contacto() -> None:
    pagina('/contact/', 'Contact | Smagnet', 'Contact Smagnet LLC: info@smagnettech.com.', f'''
<section class="cabecera-pagina"><div class="contenedor">
  <p class="antetitulo">Contact</p>
  <h1>Get in touch</h1>
  <p class="entradilla">Whether you have a question, need support or want to know how we can help, we would love to
  hear from you.</p>
</div></section>
<section class="seccion"><div class="contenedor dos">
  <div class="caja">
    <h3>Email</h3>
    <p><a class="enlace" href="mailto:{EMAIL}">{EMAIL}</a></p>
    <p>We usually reply within one business day.</p>
  </div>
  <div class="caja">
    <h3>Company</h3>
    <p>SMAGNET LLC<br>EIN: 61-2193900<br>407 Lincoln Road, Suite 12N<br>Miami Beach, FL 33139, USA</p>
  </div>
</div></section>''')


def legal() -> None:
    for ruta, titulo in [('/privacy-policy/', 'Privacy Policy'), ('/terms-and-conditions/', 'Terms and Conditions'),
                         ('/cookies-policy/', 'Cookies Policy')]:
        t = (ORIGINAL / ruta.strip('/') / 'index.html').read_text(encoding='utf-8')
        bloques = re.findall(r'<div class="et_pb_text_inner">([\s\S]*?)</div>\s*</div>', t)
        texto = max(bloques, key=len)
        texto = re.sub(r'\s(?:class|style|id)="[^"]*"', '', texto)
        texto = re.sub(r'<h1>[\s\S]*?</h1>', '', texto, count=1).strip()
        pagina(ruta, f'{titulo} | Smagnet', f'{titulo} of Smagnet LLC.', f'''
<section class="cabecera-pagina"><div class="contenedor"><h1>{html.escape(titulo)}</h1></div></section>
<section class="seccion"><div class="contenedor texto-legal">{texto}</div></section>''')


def recursos() -> None:
    a = SALIDA / 'assets'
    a.mkdir(parents=True)
    shutil.copy(RAIZ / 'src/site.css', a / 'site.css')
    shutil.copy(SUBIDAS / 'Capture-removebg-preview-1-480x457.png', a / 'logo.png')
    shutil.copy(SUBIDAS / 'augmented-reality-illustration-03@2x-980x980.png', a / 'heroe.png')
    shutil.copy(SUBIDAS / 'cropped-resize-32x32.png', a / 'icon-32.png')
    shutil.copy(SUBIDAS / 'cropped-resize-180x180.png', a / 'icon-180.png')
    shutil.copy(SUBIDAS / 'cropped-resize-270x270.png', a / 'og.png')
    shutil.copy(SUBIDAS / 'cropped-resize-32x32.png', SALIDA / 'favicon.ico')
    # Logos de las firmas de correo (Gmail los carga de aquí): Smagnet y SGMIUM.
    shutil.copytree(RAIZ / 'src/firma', a / 'firma')
    (SALIDA / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {URL}/sitemap.xml\n')
    rutas = ['/', '/services/', '/about-us/', '/get-started/', '/contact/', '/privacy-policy/',
             '/terms-and-conditions/', '/cookies-policy/']
    (SALIDA / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{URL}{r}</loc></url>\n' for r in rutas) + '</urlset>\n')


def main() -> None:
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir()
    recursos()
    inicio()
    servicios()
    sobre()
    empezar()
    contacto()
    legal()
    print('public/ generado')


if __name__ == '__main__':
    main()
