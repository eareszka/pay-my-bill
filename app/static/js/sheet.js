// Sheets stack (#248, #302): a post slides up over the feed, and its Chip in and Chat slide up over the
// post. Pulling a sheet down at the top slides it back off to the page under it. While you're on a post
// the Feed tab stays home, so tapping Feed from another tab brings you back to that post. Loaded in
// <head> without defer, so pagereveal is heard in time.
{
  const HOME = "feed-home"; // the post you were on, for the Feed tab
  const AT = "feed-at"; // where in the feed you were, for pulling the post back down
  const PULL_PX = 100;
  const isPost = (path) => /^\/posts\/\d+$/.test(path);
  const isFeed = (path) => path === "/feed";
  // The page a sheet sits on, or null when the page isn't a sheet.
  const parentOf = (path) => {
    if (isPost(path)) return "/feed";
    const child = /^(\/posts\/\d+)\/(chip-in|chat)$/.exec(path);
    return child ? child[1] : null;
  };
  const read = (key) => { try { return sessionStorage.getItem(key); } catch { return null; } };
  const write = (key, value) => {
    try {
      if (value === null) sessionStorage.removeItem(key);
      else sessionStorage.setItem(key, value);
    } catch {}
  };

  // Runs on every arrival, including Back from the cache.
  window.addEventListener("pageshow", () => {
    const { pathname, search } = window.location;
    if (isFeed(pathname)) {
      write(AT, pathname + search);
      write(HOME, null);
    } else if (isPost(pathname)) {
      write(HOME, pathname);
    }
    const page = document.querySelector("main");
    if (page) page.style.transform = "";
  });

  window.addEventListener("pagereveal", (event) => {
    if (!event.viewTransition) return;
    let from;
    try { from = new URL(window.navigation?.activation?.from?.url ?? document.referrer).pathname; } catch { return; }
    const to = window.location.pathname;
    if (parentOf(to) === from) event.viewTransition.types.add("sheet-open");
    else if (parentOf(from) === to) event.viewTransition.types.add("sheet-close");
  });

  // Back to the page under the sheet: Back in history when you came from it, else load it (for a post,
  // the feed you last saw, so you land on the same ticket). A gift error lands on Chip in again, so its
  // referrer is itself and it loads the post instead of stepping back through the form.
  const back = () => {
    const parent = parentOf(window.location.pathname);
    if (!parent) return;
    let from = null;
    try { from = new URL(document.referrer); } catch {}
    if (from?.origin === window.location.origin && from.pathname === parent) window.history.back();
    else window.location.assign(isFeed(parent) ? read(AT) || parent : parent);
  };

  const plain = (event) => !(event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0);

  // The sheet's Close (#252) does what a pull down does.
  document.addEventListener("click", (event) => {
    if (!event.target.closest?.(".sheet-close") || !plain(event)) return;
    event.preventDefault();
    back();
  });

  document.addEventListener("click", (event) => {
    const link = event.target.closest?.('.topbar > nav a[href="/feed"]');
    const home = read(HOME);
    if (!link || !home || isPost(window.location.pathname)) return;
    if (!plain(event)) return;
    event.preventDefault();
    window.location.assign(home);
  });

  // Pull a sheet down from its top to go back to the page under it.
  document.addEventListener("DOMContentLoaded", () => {
    if (!parentOf(window.location.pathname)) return;
    const page = document.querySelector("main");

    const calm = window.matchMedia("(prefers-reduced-motion: reduce)");
    const top = () => Math.max(document.body.scrollTop, document.documentElement.scrollTop) <= 0;
    let pull = null;

    document.addEventListener("touchstart", (event) => {
      const [touch] = event.touches;
      pull = event.touches.length === 1 && top() ? { x: touch.clientX, y: touch.clientY, dy: 0 } : null;
    }, { passive: true });

    document.addEventListener("touchmove", (event) => {
      if (!pull) return;
      const [touch] = event.touches;
      const dy = touch.clientY - pull.y;
      if (dy < 0 || !top() || Math.abs(touch.clientX - pull.x) > dy) {
        pull.dy = 0;
        page.style.transform = "";
        return;
      }
      pull.dy = dy;
      if (!calm.matches) page.style.transform = `translateY(${dy / 2}px)`;
    }, { passive: true });

    const release = () => {
      if (!pull) return;
      const { dy } = pull;
      pull = null;
      if (dy > PULL_PX) {
        back();
        return;
      }
      if (!dy || calm.matches) return;
      const from = page.style.transform;
      page.style.transform = "";
      page.animate?.([{ transform: from }, { transform: "none" }], { duration: 200, easing: "cubic-bezier(0.16, 1, 0.3, 1)" });
    };
    document.addEventListener("touchend", release);
    document.addEventListener("touchcancel", release);
  });
}
