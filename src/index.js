// Web estática de smagnettech.com (copia del WordPress de OVH, ver scripts/copiar-web.py).
// Solo redirige las URLs antiguas de WordPress; el resto lo sirven los assets.
const PAGINAS = { 63: '/get-started/', 52: '/about-us/', 42: '/contact/', 88: '/privacy-policy/', 95: '/terms-and-conditions/', 101: '/cookies-policy/' }

export default {
  async fetch(request, env) {
    const url = new URL(request.url)
    if (url.hostname === 'www.smagnettech.com') {
      url.hostname = 'smagnettech.com'
      return Response.redirect(url.toString(), 301)
    }
    const id = url.searchParams.get('page_id')
    if (id || url.searchParams.has('p') || url.searchParams.has('feed')) {
      return Response.redirect(`${url.origin}${PAGINAS[id] ?? '/'}`, 301)
    }
    return env.ASSETS.fetch(request)
  },
}
