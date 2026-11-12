// 한 번 본 화면과 포켓몬 그림을 태블릿에 저장해 두어서 다음부터 빨리 열려요.
// 파일을 고쳐서 다시 올릴 때는 아래 버전 숫자를 하나 올려 주세요.
const VERSION = 'v2';
const SHELL = 'shell-' + VERSION;
const IMAGES = 'images-v1';
const SHELL_FILES = ['./', 'index.html', 'pokemon-data.js', 'manifest.json', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(
    keys.filter(k => k.startsWith('shell-') && k !== SHELL).map(k => caches.delete(k))
  )).then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // 포켓몬 그림: 저장된 게 있으면 바로 보여 주고, 없으면 받아서 저장
  if (url.hostname === 'raw.githubusercontent.com' && url.pathname.endsWith('.png')) {
    e.respondWith(caches.open(IMAGES).then(async c => {
      const hit = await c.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok || res.type === 'opaque') c.put(req, res.clone());
      return res;
    }));
    return;
  }

  // 도감 화면: 인터넷이 되면 새 버전, 안 되면 저장된 버전
  if (url.origin === location.origin) {
    e.respondWith(fetch(req).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(SHELL).then(c => c.put(req, copy)); }
      return res;
    }).catch(() => caches.match(req, { ignoreSearch: true })));
  }
  // 울음소리는 그대로 인터넷에서 받아요
});
