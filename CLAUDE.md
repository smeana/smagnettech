# smagnettech.com

Web estática de SMAGNET LLC (servicios de software, datos, IA, Amazon Ads, cloud y fintech) en Cloudflare Workers
(assets estáticos). Sustituye al WordPress + Divi del alojamiento de OVH (2026-10-12).

```
scripts/generar.py     # genera public/ (HTML + CSS). Textos de servicios: CV del titular (~/Documents/CV)
scripts/copiar-web.py  # copia del WordPress original en original/ (de ahí salen imágenes y textos legales)
src/site.css           # estilos (se copian a public/assets/site.css)
src/index.js           # Worker: redirige www y las URLs antiguas de WordPress (?page_id=N) con 301
original/              # copia estática del WordPress tal como estaba (referencia, no se publica)
public/                # GENERADO: no editar a mano
```

- Cambiar algo: editar `scripts/generar.py` o `src/site.css` → `python3 scripts/generar.py` →
  `npx wrangler@4 dev --port 8790` para verlo → `npx wrangler@4 deploy`.
- Cuenta Cloudflare sergiomeana20@gmail.com, Worker `smagnettech` con dominios propios `smagnettech.com` y `www`
  (www → 301 en `src/index.js`) desde el 2026-10-12; también en https://smagnettech.sergiomeana20.workers.dev.
- Sin formularios ni cookies propias: el contacto es `mailto:info@smagnettech.com`. Fuentes de Google Fonts.

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

- [ ] Después, cancelar el alojamiento web de OVH (borra el WordPress: la copia está en `original/`).
