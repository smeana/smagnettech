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
LINKEDIN = 'https://www.linkedin.com/company/smagnet/'

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

# Logo de LinkedIn (círculo azul con «in»), en línea como el resto de iconos.
ICONO_LINKEDIN = ('<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><circle cx="12" cy="12" r="12" '
                  'fill="#0a66c2"/><g fill="#fff" transform="translate(-1.2 0)"><circle cx="8" cy="7.2" r="1.6"/>'
                  '<rect x="6.6" y="9.6" width="2.8" height="8"/><path d="M11.2 9.6h2.7v1.2c.5-.9 1.6-1.5 2.9-1.5 '
                  '2.4 0 3 1.5 3 3.7v4.6h-2.8v-4.1c0-1-.2-1.9-1.3-1.9s-1.7.8-1.7 1.9v4.1h-2.8z"/></g></svg>')

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
    <a class="logo" href="/" aria-label="Smagnet home"><img src="/assets/logo-texto.png" alt="Smagnet" width="168" height="40"></a>
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
      <img src="/assets/logo-texto.png" alt="" width="152" height="36">
      <p><strong>SMAGNET LLC</strong><br>EIN: 61-2193900<br>407 Lincoln Road, Suite 12N<br>Miami Beach, FL 33139</p>
    </div>
    <div>
      <h4>Services</h4>
      {''.join(f'<a href="/services/#{s["id"]}">{s["titulo"]}</a>' for s in SERVICIOS)}
    </div>
    <div>
      <h4>Get in touch</h4>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
      <a href="/contact/">Contact form</a>
      <a href="/get-started/">Free consultation</a>
      <a class="pie__social" href="{LINKEDIN}" target="_blank" rel="noopener">{ICONO_LINKEDIN}LinkedIn</a>
    </div>
    <div>
      <h4>Company</h4>
      <a href="/sustainability/">Sustainability (SDGs)</a>
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
           'Smagnet is a software and data engineering consultancy in Miami Beach, Florida, building reliable, '
           'data-intensive systems for finance, fintech and e-commerce.', f'''
<section class="cabecera-pagina"><div class="contenedor">
  <p class="antetitulo">About Smagnet</p>
  <h1>Engineering for systems that have to work</h1>
  <p class="entradilla">Smagnet is a software and data engineering consultancy based in Miami Beach, Florida. We design,
  build and run data-intensive systems for companies where reliability, latency and data quality have a direct impact
  on revenue.</p>
</div></section>
<section class="seccion"><div class="contenedor dos">
  <div>
    <h2>Our experience</h2>
    <p>Our team brings more than 12 years of hands-on experience as architects, data engineers and quantitative
    developers, delivering production systems for investment banks, payment processors, asset managers, crypto
    exchanges, e-commerce brands and public institutions across the US and Europe.</p>
    <p>Representative work:</p>
    <ul class="lista">
      <li>Payment platforms and event-driven Kafka architectures for a global bank</li>
      <li>Pricing libraries and data platforms for a European banking group</li>
      <li>Real-time ETF valuation (iNAV) for an electronic trading venue</li>
      <li>Machine-learning risk models for a global investment bank</li>
      <li>A 120 TB data platform migration to Google Cloud, with demand forecasting, for an automotive manufacturer</li>
      <li>Azure data architecture for an EU agency</li>
      <li>Low-latency market making connected to 30+ crypto exchanges</li>
      <li>Amazon advertising and marketplace automation for brands selling in 11 countries</li>
    </ul>
  </div>
  <div class="caja">
    <h3>Certifications</h3>
    <ul><li>Google Cloud Certified Data Engineer</li><li>Microsoft Azure Fundamentals (AZ-900)</li>
    <li>Microsoft Azure Data Fundamentals (DP-900)</li></ul>
    <h3>Industries</h3>
    <ul><li>Banking and capital markets</li><li>Payments and fintech</li><li>Crypto and digital assets</li>
    <li>E-commerce and Amazon sellers</li><li>Automotive</li><li>Public sector (EU)</li></ul>
    <h3>Languages</h3>
    <ul><li>English</li><li>Spanish</li></ul>
  </div>
</div></section>
<section class="seccion seccion--gris"><div class="contenedor">
  <h2>How we work</h2>
  <div class="tres">
    <div><h3>Senior engineering</h3><p>The engineers who scope your project are the ones who build it. No hand-offs to
    junior teams.</p></div>
    <div><h3>Clear scope and cost</h3><p>Every engagement starts with a free consultation and a written proposal covering
    scope, architecture, timeline and cost.</p></div>
    <div><h3>Built for production</h3><p>We deliver in short iterations, document what we build so your team can own it,
    and support it in production.</p></div>
  </div>
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


# Formulario de contacto: lo recibe el Worker (POST /api/contact, src/index.js) y lo envía por correo a info@.
# Con JS se envía con fetch y se muestra el resultado en la página; sin JS, el Worker redirige a /contact/thanks/.
FORM_JS = '''<script>
document.querySelector('.formulario').addEventListener('submit', async e => {
  e.preventDefault()
  const f = e.currentTarget, estado = f.querySelector('.formulario__estado'), boton = f.querySelector('button')
  boton.disabled = true; boton.textContent = 'Sending…'; estado.className = 'formulario__estado'; estado.textContent = ''
  try {
    const r = await fetch(f.action, { method: 'POST', body: new FormData(f), headers: { Accept: 'application/json' } })
    const d = await r.json().catch(() => ({}))
    if (!r.ok) throw new Error(d.error || 'The message could not be sent.')
    f.reset(); estado.className = 'formulario__estado ok'
    estado.textContent = 'Thank you! We have received your message and will reply within one business day.'
  } catch (err) {
    estado.className = 'formulario__estado error'
    estado.textContent = err.message + ' You can also write to us at {EMAIL}.'
  }
  boton.disabled = false; boton.textContent = 'Send message'
})
</script>'''


def contacto() -> None:
    temas = ''.join(f'<option>{s["titulo"]}</option>' for s in SERVICIOS)
    pagina('/contact/', 'Contact | Smagnet',
           'Contact Smagnet LLC: tell us about your project and we will reply within one business day.', f'''
<section class="cabecera-pagina"><div class="contenedor">
  <p class="antetitulo">Contact</p>
  <h1>Get in touch</h1>
  <p class="entradilla">Whether you have a question, need support or want to know how we can help, we would love to
  hear from you.</p>
</div></section>
<section class="seccion"><div class="contenedor contacto">
  <form class="formulario caja" action="/api/contact" method="post">
    <div class="formulario__fila">
      <label>Name<input name="name" type="text" required maxlength="120" autocomplete="name"></label>
      <label>Email<input name="email" type="email" required maxlength="200" autocomplete="email"></label>
    </div>
    <div class="formulario__fila">
      <label><span>Company <em>(optional)</em></span><input name="company" type="text" maxlength="120" autocomplete="organization"></label>
      <label>Topic
        <select name="topic" required>
          <option value="" disabled selected>Choose one</option>{temas}<option>Other</option>
        </select>
      </label>
    </div>
    <label>Message<textarea name="message" required minlength="10" maxlength="5000" rows="7"
      placeholder="Tell us about your project, goals and timeline"></textarea></label>
    <!-- trampa antispam: invisible para las personas -->
    <input class="trampa" name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true">
    <label class="formulario__check"><input name="consent" type="checkbox" required>
      <span>I agree to the <a href="/privacy-policy/">Privacy Policy</a> and to Smagnet using my data only to reply to
      this message.</span></label>
    <button class="boton" type="submit">Send message</button>
    <p class="formulario__estado" role="status" aria-live="polite"></p>
  </form>
  <aside>
    <div class="caja">
      <h3>Email</h3>
      <p><a class="enlace" href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p>We usually reply within one business day.</p>
      <h3>Company</h3>
      <p>SMAGNET LLC<br>EIN: 61-2193900<br>407 Lincoln Road, Suite 12N<br>Miami Beach, FL 33139, USA</p>
    </div>
  </aside>
</div></section>
{FORM_JS.replace('{EMAIL}', EMAIL)}''')
    pagina('/contact/thanks/', 'Message sent | Smagnet', 'Your message has been sent to Smagnet.', '''
<section class="cabecera-pagina"><div class="contenedor">
  <p class="antetitulo">Contact</p>
  <h1>Thank you!</h1>
  <p class="entradilla">We have received your message and will reply within one business day.</p>
  <div class="botones"><a class="boton" href="/">Back to home</a></div>
</div></section>
<section class="seccion"></section>''')


# Objetivos de Desarrollo Sostenible con los que se alinea el trabajo (sin aval ni certificación de la ONU), como las
# páginas de compromiso de marketbycrypto y aerovik. Sin adjetivos verdes: solo lo que se hace de verdad.
ODS_URL = 'https://sdgs.un.org/goals'
ODS = [
    ('9', 'Industry, Innovation and Infrastructure',
     'We build reliable, well-documented digital infrastructure (data platforms, APIs and cloud systems) that our '
     'clients can run and evolve for years, not throwaway prototypes.'),
    ('8', 'Decent Work and Economic Growth',
     'We automate repetitive work (reporting, stock control, campaign management) so teams spend their time on '
     'decisions, and we help small sellers compete in global marketplaces.'),
    ('12', 'Responsible Consumption and Production',
     'We extend and modernize existing systems before rewriting them, and we size infrastructure for real demand '
     'instead of buying capacity that sits idle.'),
    ('13', 'Climate Action',
     'Efficient code and right-sized cloud resources use less energy. We review idle servers, oversized clusters and '
     'unnecessary data processing in every project, which lowers both the bill and the carbon footprint.'),
]


def sostenibilidad() -> None:
    ods = ''.join(f'<article class="tarjeta"><p class="antetitulo">SDG {n}</p><h3>{t}</h3><p>{d}</p></article>'
                  for n, t, d in ODS)
    pagina('/sustainability/', 'Our Commitment to the SDGs | Smagnet',
           'How Smagnet aligns its software, data and cloud work with the UN Sustainable Development Goals, and how '
           'we keep the carbon footprint of our systems and this website low.', f'''
<section class="cabecera-pagina"><div class="contenedor">
  <p class="antetitulo">Sustainability</p>
  <h1>Our commitment to the SDGs</h1>
  <p class="entradilla">We align our work with the <a href="{ODS_URL}" target="_blank" rel="noopener">Sustainable
  Development Goals</a> of the United Nations 2030 Agenda, applied to what we actually do: building software, data
  and cloud systems.</p>
</div></section>
<section class="seccion"><div class="contenedor">
  <div class="rejilla rejilla--dos">{ods}</div>
  <p class="nota">Smagnet LLC is not endorsed or certified by the United Nations. This page explains how we align our
  work with its goals.</p>
</div></section>
<section class="seccion seccion--gris"><div class="contenedor dos">
  <div>
    <h2>Carbon footprint</h2>
    <p>Software has a physical cost: every server, query and page view uses electricity. In client projects we treat
    efficiency as a requirement:</p>
    <ul class="lista">
      <li>Right-sizing and auto-scaling cloud resources, and switching off idle environments.</li>
      <li>Processing only the data that is needed, incrementally instead of full reloads.</li>
      <li>Choosing efficient languages and architectures (for example Rust for hot paths) where it matters.</li>
      <li>Choosing cloud regions and providers that report their energy sources.</li>
    </ul>
  </div>
  <div class="caja">
    <h3>This website</h3>
    <ul>
      <li>Static pages served from Cloudflare’s edge network: no application servers or databases running for it.</li>
      <li>No tracking scripts, advertising cookies or analytics.</li>
      <li>Light pages with optimized images and a single stylesheet.</li>
    </ul>
    <p>You can check the estimated emissions of any page with the
    <a href="https://www.websitecarbon.com/" target="_blank" rel="noopener">Website Carbon Calculator</a>.</p>
  </div>
</div></section>
{cta()}''')


# La política original decía que no se recogían datos; desde que hay formulario de contacto, se explica qué se hace.
PRIVACIDAD_ORIGINAL = ('<h4><strong>1. No Collection of Personal Data</strong></h4>\n<p>We do not collect, store, or '
                       'process any personal information from users on this website. This includes data from forms, '
                       'sign-ups, user accounts, or payments.</p>')
PRIVACIDAD_FORMULARIO = (
    '<h4><strong>1. Personal Data</strong></h4>\n<p>We only process the personal data you send us through the '
    f'<a href="/contact/">contact form</a> or by email: your name, email address, company (optional) and message. We '
    'use it only to reply to you and to follow up on your request, we do not store it in a database on this website '
    f'(the form is delivered by email to {EMAIL}), and we do not share it with third parties or use it for marketing. '
    f'You can ask us to delete your messages at any time by writing to {EMAIL}. The website has no user accounts, '
    'sign-ups or payments.</p>')


def legal() -> None:
    for ruta, titulo in [('/privacy-policy/', 'Privacy Policy'), ('/terms-and-conditions/', 'Terms and Conditions'),
                         ('/cookies-policy/', 'Cookies Policy')]:
        t = (ORIGINAL / ruta.strip('/') / 'index.html').read_text(encoding='utf-8')
        bloques = re.findall(r'<div class="et_pb_text_inner">([\s\S]*?)</div>\s*</div>', t)
        texto = max(bloques, key=len)
        texto = re.sub(r'\s(?:class|style|id)="[^"]*"', '', texto)
        texto = re.sub(r'<h1>[\s\S]*?</h1>', '', texto, count=1).strip()
        if ruta == '/privacy-policy/':
            texto = texto.replace(PRIVACIDAD_ORIGINAL, PRIVACIDAD_FORMULARIO)
            assert PRIVACIDAD_FORMULARIO in texto, 'cambió el texto de la política de privacidad original'
        pagina(ruta, f'{titulo} | Smagnet', f'{titulo} of Smagnet LLC.', f'''
<section class="cabecera-pagina"><div class="contenedor"><h1>{html.escape(titulo)}</h1></div></section>
<section class="seccion"><div class="contenedor texto-legal">{texto}</div></section>''')


def recursos() -> None:
    a = SALIDA / 'assets'
    a.mkdir(parents=True)
    shutil.copy(RAIZ / 'src/site.css', a / 'site.css')
    shutil.copy(RAIZ / 'src/img/logo-96.png', a / 'logo.png')  # 96 px. Logos e iconos: scripts/logo.py
    shutil.copy(RAIZ / 'src/img/logo-texto.png', a / 'logo-texto.png')  # horizontal: cabecera y pie
    shutil.copy(SUBIDAS / 'augmented-reality-illustration-03@2x-980x980.png', a / 'heroe.png')
    for f in ('icon-32.png', 'icon-180.png', 'og.png'):
        shutil.copy(RAIZ / 'src/img' / f, a / f)
    shutil.copy(RAIZ / 'src/img/favicon.ico', SALIDA / 'favicon.ico')
    # Logos de las firmas de correo (Gmail los carga de aquí): Smagnet y SGMIUM.
    shutil.copytree(RAIZ / 'src/firma', a / 'firma')
    (SALIDA / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {URL}/sitemap.xml\n')
    rutas = ['/', '/services/', '/about-us/', '/get-started/', '/contact/', '/sustainability/', '/privacy-policy/',
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
    sostenibilidad()
    legal()
    print('public/ generado')


if __name__ == '__main__':
    main()
