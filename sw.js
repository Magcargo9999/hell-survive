/* v9.68 그림 캐시: src/assets/ 의 그림은 주소에 내용 해시(?v=)가 붙어 있어 바뀌면 주소도 바뀐다 → 한 번 받으면 다음 접속부터는 네트워크 없이 바로 쓴다 */
const CACHE = 'hs-assets-v1';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== self.location.origin || !u.pathname.includes('/src/assets/') || !u.search.includes('v=')) return;
  e.respondWith(caches.open(CACHE).then(c => c.match(r).then(hit => hit || fetch(r).then(res => {
    if (res && res.ok) {
      const copy = res.clone();
      c.put(r, copy).then(() => c.keys()).then(ks => ks.forEach(k => { if (k.url !== r.url && k.url.split('?')[0] === r.url.split('?')[0]) c.delete(k); })).catch(() => {});   // 같은 그림의 옛 판은 지운다
    }
    return res;
  }))));
});
