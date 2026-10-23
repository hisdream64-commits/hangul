/* 한글 교실 고급반 — 오프라인 서비스 워커
   빌드 때 7fe48dfa47 이 실제 값으로 바뀝니다(go/tools/build_audio_bundle_go.py).

   - 이 워커가 맡는 범위는 /go/ 안쪽뿐입니다(파일이 /go/sw.js 에 있어 저절로 그렇게 됩니다).
     기초반(/)은 뿌리의 sw.js 가 따로 맡습니다.
   - 화면(index.html 등)은 인터넷이 되면 새것을 먼저 받고, 안 되면 저장해 둔 것을 씁니다.
   - 소리는 audio/audio.bin 한 덩어리로 저장합니다. 한 번 저장하면 그대로 씁니다.
   - 낱개 mp3(audio/v*.mp3)는 묶음을 받기 전에 인터넷으로 그때그때 듣는 용도입니다.
     낱개로 저장하면 파일마다 붙는 관리 정보 때문에 저장공간이 빠듯한 기기에서
     일부가 조용히 빠집니다. 그래서 낱개는 저장하지 않습니다.

   ⚠️ 캐시 저장소는 주소(urihangul.vercel.app) 하나를 기초반과 함께 씁니다.
      그래서 묵은 캐시를 치울 때 'hangul3-' 로 시작하는 제 것만 건드립니다.
      기초반 것('hangul-...')을 지우면 기초반이 오프라인에서 먹통이 됩니다.
      (뿌리 sw.js 에도 같은 이유로 짝이 되는 장치가 들어 있습니다)
*/
'use strict';

var PREFIX = 'hangul3-';
var SHELL = 'hangul3-shell-7fe48dfa47';
var AUDIO = 'hangul3-audio';                 // 판이 바뀌어도 그대로 둔다
var KEEP = [SHELL, AUDIO];

var SHELL_FILES = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-180.png',
  './icon-192.png',
  './icon-512.png',
  './icon-512-maskable.png'
];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(SHELL)
      .then(function (c) { return c.addAll(SHELL_FILES); })
      .catch(function () { /* 한 개라도 실패해도 설치는 진행 */ })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys()
      .then(function (names) {
        return Promise.all(names.map(function (n) {
          // 제 이름표가 붙은 것 가운데 묵은 것만 치웁니다.
          var mine = n.indexOf(PREFIX) === 0;
          return (mine && KEEP.indexOf(n) === -1) ? caches.delete(n) : null;
        }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

var BUNDLE = 'audio/audio.bin';

function isAudio(url) {
  return url.pathname.indexOf('/audio/') !== -1;
}
function isBundle(url) {
  return url.pathname.indexOf(BUNDLE) !== -1;
}

// 낱개 mp3: 이미 저장해 둔 것이 있으면 그걸 쓰고, 없으면 받아 오되 저장은 하지 않는다.
function cacheReadOnly(req, cacheName) {
  return caches.open(cacheName).then(function (c) {
    return c.match(req).then(function (hit) {
      return hit || fetch(req);
    });
  });
}

// 소리 묶음·아이콘: 저장해 둔 것 먼저 (없으면 받아서 저장)
function cacheFirst(req, cacheName) {
  return caches.open(cacheName).then(function (c) {
    return c.match(req).then(function (hit) {
      if (hit) return hit;
      return fetch(req).then(function (res) {
        if (res && res.ok) c.put(req, res.clone());
        return res;
      });
    });
  });
}

// 화면: 인터넷 먼저(4초까지 기다림), 안 되면 저장해 둔 것
function networkFirst(req) {
  return caches.open(SHELL).then(function (c) {
    var fromNet = fetch(req).then(function (res) {
      if (res && res.ok) c.put(req, res.clone());
      return res;
    });
    var timeout = new Promise(function (resolve) {
      setTimeout(function () { resolve(null); }, 4000);
    });
    return Promise.race([fromNet.catch(function () { return null; }), timeout])
      .then(function (res) {
        if (res) return res;
        return c.match(req).then(function (hit) {
          // './index.html' 은 이 파일 자리(/go/) 기준이라 고급반 화면입니다.
          return hit || c.match('./index.html') || fromNet;
        });
      });
  });
}

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;

  var url;
  try { url = new URL(req.url); } catch (err) { return; }
  if (url.origin !== self.location.origin) return;

  if (isBundle(url) || /\.(png|webmanifest)$/.test(url.pathname)) {
    e.respondWith(cacheFirst(req, isBundle(url) ? AUDIO : SHELL));
    return;
  }
  if (isAudio(url)) {
    e.respondWith(cacheReadOnly(req, AUDIO));
    return;
  }
  if (req.mode === 'navigate' || /\.html$/.test(url.pathname) || url.pathname.endsWith('/')) {
    e.respondWith(networkFirst(req));
  }
});
