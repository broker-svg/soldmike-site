// Keeps the open house app opening without internet: the page shell is cached; sign-ins queue on the phone.
const C = 'oh-v3';
const SHELL = ['/open-house/', '/assets/listings.js?v=3', '/logo-soldmike-white.png', '/mike.png', '/open-house/icon-192.png'];
self.addEventListener('install', e => e.waitUntil(caches.open(C).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== C).map(x => caches.delete(x)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin) return;
  // network first (always fresh when online), cache as fallback
  e.respondWith(fetch(e.request).then(r => { const copy = r.clone(); caches.open(C).then(c => c.put(e.request, copy)); return r; })
    .catch(() => caches.match(e.request, { ignoreSearch: u.pathname === '/open-house/' })));
});
