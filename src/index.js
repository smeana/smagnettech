// Web estática de smagnettech.com (copia del WordPress de OVH, ver scripts/copiar-web.py).
// Redirige las URLs antiguas de WordPress, recibe el formulario de contacto (POST /api/contact) y el resto lo
// sirven los assets.
// Parámetros de WordPress que Google aún rastrea (?p=1, ?feed=rss2, ?cat=1…): 301 a la portada, no copia con 200.
const PARAMS_WP = ['p', 'feed', 'cat', 'author', 's', 'attachment_id', 'tag', 'm', 'preview']
const PAGINAS = { 63: '/get-started/', 52: '/about-us/', 42: '/contact/', 88: '/privacy-policy/', 95: '/terms-and-conditions/', 101: '/cookies-policy/' }

// Los mensajes del formulario llegan a info@ (alias de Google Workspace); «Responder» contesta a quien escribió.
const DESTINO = 'info@smagnettech.com'
const REMITENTE = { email: 'info@smagnettech.com', name: 'Smagnet web' }
const EMAIL_RE = /^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]{2,}$/

export default {
  async fetch(request, env) {
    const url = new URL(request.url)
    // www y *.workers.dev → dominio principal (evita contenido duplicado en Google).
    if (url.hostname === 'www.smagnettech.com' || url.hostname.endsWith('.workers.dev')) {
      url.hostname = 'smagnettech.com'
      return Response.redirect(url.toString(), 301)
    }
    if (url.pathname === '/api/contact') return contacto(request, env)
    const id = url.searchParams.get('page_id')
    if (id || PARAMS_WP.some(p => url.searchParams.has(p))) {
      return Response.redirect(`${url.origin}${PAGINAS[id] ?? '/'}`, 301)
    }
    return env.ASSETS.fetch(request)
  },
}

async function contacto(request, env) {
  if (request.method !== 'POST') return new Response('Method not allowed', { status: 405, headers: { Allow: 'POST' } })
  const json = (request.headers.get('Accept') || '').includes('application/json')
  const responder = (status, error) =>
    json
      ? Response.json(error ? { error } : { ok: true }, { status })
      : error
        ? new Response(error, { status, headers: { 'Content-Type': 'text/plain; charset=utf-8' } })
        : Response.redirect(new URL('/contact/thanks/', request.url).toString(), 303)

  // Solo desde la propia web (evita que otras páginas o scripts usen el formulario): los navegadores siempre mandan
  // Origin en un POST; sin él, o desde otro sitio, se rechaza.
  const origen = request.headers.get('Origin')
  if (!origen || new URL(origen).hostname !== new URL(request.url).hostname) return responder(403, 'Forbidden.')

  const ip = request.headers.get('CF-Connecting-IP') || 'local'
  if (env.LIMITE && !(await env.LIMITE.limit({ key: ip })).success) {
    return responder(429, 'Too many messages in a short time. Please try again in a minute.')
  }

  let f
  try {
    f = await request.formData()
  } catch {
    return responder(400, 'Invalid form.')
  }
  const campo = (k, max) => String(f.get(k) ?? '').trim().slice(0, max)
  const d = {
    name: campo('name', 120),
    email: campo('email', 200),
    company: campo('company', 120),
    topic: campo('topic', 120),
    message: campo('message', 5000),
  }
  // Trampa antispam: los bots rellenan el campo oculto «website»; se responde como si se hubiera enviado.
  if (campo('website', 200)) return responder(200)
  // Cloudflare Turnstile (widget «smagnettech.com contacto»; secreto en `wrangler secret`, en local .dev.vars con la
  // clave de prueba): sin un token válido de un navegador real no se envía nada.
  if (!(await humano(f.get('cf-turnstile-response'), ip, env))) {
    return responder(403, 'Please complete the anti-spam check and try again.')
  }
  // El spam suele venir cargado de enlaces: con más de 3 se descarta en silencio.
  if ((d.message.match(/https?:\/\/|www\./gi) || []).length > 3) return responder(200)
  if (!d.name || !EMAIL_RE.test(d.email) || d.message.length < 10) {
    return responder(400, 'Please fill in your name, a valid email and a message of at least 10 characters.')
  }
  if (!f.get('consent')) return responder(400, 'Please accept the Privacy Policy.')

  if (!env.EMAIL) {
    console.error('[contacto] falta el binding send_email «EMAIL»: no se envía')
    return responder(503, 'The form is temporarily unavailable.')
  }
  const filas = [['Name', d.name], ['Email', d.email], ['Company', d.company || '—'], ['Topic', d.topic || '—']]
  const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c])
  try {
    const r = await env.EMAIL.send({
      from: REMITENTE,
      to: DESTINO,
      replyTo: { email: d.email, name: d.name },
      subject: `[smagnettech.com] ${d.topic || 'Contact'} — ${d.name}`,
      text: `${filas.map(([k, v]) => `${k}: ${v}`).join('\n')}\n\n${d.message}\n`,
      html:
        `<table cellpadding="4" style="font:14px/1.5 Arial,sans-serif">${filas.map(([k, v]) => `<tr><td><b>${k}</b></td><td>${esc(v)}</td></tr>`).join('')}</table>` +
        `<p style="font:14px/1.6 Arial,sans-serif;white-space:pre-wrap">${esc(d.message)}</p>`,
    })
    console.log(`[contacto] enviado (${r?.messageId ?? 'sin id'})`)
  } catch (e) {
    console.error('[contacto] error al enviar:', e)
    return responder(502, 'The message could not be sent.')
  }
  return responder(200)
}

async function humano(token, ip, env) {
  if (!token || !env.TURNSTILE_SECRET) return false
  const body = new FormData()
  body.append('secret', env.TURNSTILE_SECRET)
  body.append('response', String(token))
  if (ip !== 'local') body.append('remoteip', ip)
  try {
    const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', { method: 'POST', body })
    const v = await r.json()
    if (!v.success) console.log('[contacto] Turnstile rechazado:', v['error-codes'])
    return v.success === true
  } catch (e) {
    console.error('[contacto] Turnstile no responde:', e)
    return false
  }
}
