// Fetch the pages one tap away (#219), so Next and Back open from the browser's cache.
// Safari ignores <link rel="prefetch">, so there fetch() does the same job.
const warm = () => {
  for (const link of document.querySelectorAll('link[rel="prefetch"]')) {
    fetch(link.href, { credentials: "same-origin", priority: "low" }).catch(() => {});
  }
};
if (!document.createElement("link").relList.supports("prefetch")) {
  if (document.readyState === "complete") warm();
  else window.addEventListener("load", warm, { once: true });
}
