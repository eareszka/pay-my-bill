// Offline fallback only (#185). Pages and data always come from the network, so
// nobody sees a stale ask or gift; the cache just covers having no connection.
const CACHE = "pmb-offline-v1";
const OFFLINE = "/offline";
const PRECACHE = [
  OFFLINE,
  "/static/css/app.css",
  "/static/fonts/league-gothic-400.woff2",
  "/static/fonts/public-sans-400.woff2",
  "/static/fonts/public-sans-700.woff2",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  if (request.mode === "navigate") {
    event.respondWith(fetch(request).catch(() => caches.match(OFFLINE)));
    return;
  }
  const url = new URL(request.url);
  if (url.origin === self.location.origin && url.pathname.startsWith("/static/")) {
    event.respondWith(fetch(request).catch(() => caches.match(request)));
  }
});
