# smagnettech.com

Web estática de SMAGNET LLC (servicios de software, datos, IA, Amazon Ads, cloud y fintech) en Cloudflare Workers
(assets estáticos). Sustituye al WordPress + Divi del alojamiento de OVH (2026-10-12).

```
scripts/generar.py     # genera public/ (HTML + CSS). Textos de servicios: CV del titular (~/Documents/CV)
scripts/copiar-web.py  # copia del WordPress original en original/ (de ahí salen imágenes y textos legales)
src/site.css           # estilos (se copian a public/assets/site.css)
media/                 # logos (original 512 px y cuadrado para LinkedIn: scripts/logo-linkedin.py) y portada de LinkedIn (scripts/portada-linkedin.py); no se publica
src/index.js           # Worker: redirige www y las URLs antiguas de WordPress (?page_id=N) con 301 y recibe el formulario
src/img/               # imágenes propias de la web (logo de 96 px de la cabecera)
original/              # copia estática del WordPress tal como estaba (referencia, no se publica)
public/                # GENERADO: no editar a mano
```

- Cambiar algo: editar `scripts/generar.py` o `src/site.css` → `python3 scripts/generar.py` →
  `npx wrangler@4 dev --port 8790` para verlo → `npx wrangler@4 deploy`.
- Cuenta Cloudflare sergiomeana20@gmail.com, Worker `smagnettech` con dominios propios `smagnettech.com` y `www`
  (www → 301 en `src/index.js`) desde el 2026-10-12; también en https://smagnettech.sergiomeana20.workers.dev.
- **LinkedIn**: página de empresa https://www.linkedin.com/company/smagnet/ (ID 146739915, creada el 2026-10-14;
  enlazada en el pie). El titular la administra pero **debe quedar oculto**: no poner su nombre en la web ni en la
  página, no añadirla como experiencia en su perfil, no invitar contactos y publicar siempre como Smagnet.
- Sin cookies propias. Fuentes de Google Fonts. **Formulario de contacto** en `/contact/` → `POST /api/contact`
  (`src/index.js`): valida, trampa antispam (`website`), límite 5/min por IP (ratelimit namespace 1006) y lo envía
  con **Cloudflare Email Sending** (binding `send_email` «EMAIL», remitente `info@`, «Responder» va a quien escribe).
  Dominio dado de alta en Email Service → Email Sending el 2026-10-14 (sending subdomain `9e360c37008d4823824e26286dc59f2a`,
  registros `cf-bounce`, no tocan Google; **no** aplicar el DMARC `p=reject` que sugiere: el nuestro es `p=quarantine`).
  Probado en producción el 2026-10-14: llega a la bandeja de entrada de smeana@sgmium.com en 1 s con SPF, DKIM
  (`smagnettech.com`) y DMARC en `pass`. Solo acepta envíos desde la propia web (cabecera `Origin`). En local los
  correos van a `.wrangler/tmp/email/`.
  La política de privacidad se reescribe en `generar.py` (PRIVACIDAD_FORMULARIO) para explicar el formulario.
- `/sustainability/`: compromiso con los ODS (9, 8, 12, 13) y huella de carbono, como en marketbycrypto/aerovik;
  enlazada desde el pie. Sin aval de la ONU (se dice en la página).

## DNS y correo

- Registrador: OVH. DNS: zona de Cloudflare (cuenta sergiomeana20, NS coby/novalee) desde el 2026-10-12. Los DKIM
  (`google._domainkey`) van en «DNS only».
- **Correo en Google Workspace** desde el 2026-10-12 (antes Proton, ya retirado: dominio quitado de la cuenta de Proton
  y borrados sus registros). MX `smtp.google.com` (1); SPF `v=spf1 include:_spf.google.com ~all`; DKIM
  `google._domainkey` (2048 bits); DMARC `p=quarantine` (informes a `info@`); MTA-STS (Worker `mta-sts` de `~/code/marketbycrypto/infra/mta-sts/`) y TLS-RPT. `account@` (avisos de Payoneer) e `info@smagnettech.com` son
  alias de `smeana@sgmium.com`; el correo antiguo sigue en Proton.
- **Firmas de correo**: `src/firma/` (logos de Smagnet y de SGMIUM; `generar.py` los copia a `/assets/firma/`).
  Gmail los carga de https://smagnettech.com/assets/firma/… — **no borrarlos ni renombrarlos** o las firmas de
  Gmail (Smagnet y SGMIUM) se quedan sin logo. Firma «Smagnet» en inglés con el pie de SMAGNET LLC.

## Pendiente

- [x] Zona de Cloudflare limpia de restos de OVH (`ftp`, TXT `1|www…` y `3|welcome` borrados el 2026-10-14).
- [x] Baja inmediata en OVH (cuenta gs832990-ovh) del alojamiento Perso `smagneu.cluster027.hosting.ovh.net`
  (incluye la BD `smagneu375`, el MX Plan y la redirección `postmaster@`; el WordPress está copiado en `original/`)
  y de la zona DNS de OVH de `smagnettech.com` (no se usa: los NS son de Cloudflare). Baja pedida el 2026-10-14
  (quedó «al vencimiento», 2027-09-01) y baja inmediata confirmada el mismo día (alojamiento y MX Plan
  `terminated`) + ticket de reembolso de la renovación (factura ES4415232, 71,88 € sin IVA). Zona DNS de OVH:
  baja confirmada 2026-10-14 (`terminated`). VPS, vRack, Public Cloud y las demás zonas de OVH también dadas de baja.
- Zona Cloudflare: «Always Use HTTPS» activado y TLS mínimo 1.2 (2026-10-14). DNSSEC desactivado en Cloudflare y
  en OVH (coherente); si se activa, el DS se pone en OVH o se deja para después de transferir el dominio.
- [ ] **Dominio**: sigue en OVH (renovación automática, caduca el 2027-06-10). Transferirlo a Cloudflare Registrar
  **antes** de esa fecha (p. ej. en abril-mayo de 2027): desbloquear en OVH, pedir el AuthCode, iniciar la
  transferencia en Cloudflare (cobra 1 año, que se suma a la caducidad). Después, quitar la renovación en OVH.
