// How it works (#120): name each move for the page transition, and let a swipe or the arrow keys
// take Back and Next. Every step is an ordinary link, so the stories work the same without this.
// Loaded in <head> without defer, on the doors page too, so pagereveal is heard before the first frame.
// The doors count as step 0 of both stories.
const stepOf = (url) => {
  const { pathname } = new URL(url);
  if (pathname === "/") return { path: null, step: 0 };
  const match = pathname.match(/^\/how\/(help|ask)(?:\/(\d+))?$/);
  return match ? { path: match[1], step: Number(match[2] || 1) } : null;
};

// Opening a door, or swapping to the other story, lets the field land before the words cut in.
// Going back cuts in from the left.
window.addEventListener("pagereveal", (event) => {
  const from = window.navigation?.activation?.from?.url;
  if (!event.viewTransition || !from) return;
  const was = stepOf(from);
  const now = stepOf(window.location.href);
  if (!was || !now) return;
  if (was.step > now.step && (was.path === now.path || !now.path)) event.viewTransition.types.add("back");
  else if (was.path !== now.path) event.viewTransition.types.add("open");
});

const SWIPE_PX = 60;

document.addEventListener("DOMContentLoaded", () => {
  const field = document.querySelector(".how-field");
  const next = document.querySelector(".how-next");
  const back = document.querySelector(".how-back");
  if (!field) return;
  const go = (link) => link && window.location.assign(link.href);

  let start = null;
  field.addEventListener("pointerdown", (event) => {
    if (event.pointerType !== "mouse") start = { x: event.clientX, y: event.clientY };
  });
  field.addEventListener("pointercancel", () => { start = null; });
  field.addEventListener("pointerup", (event) => {
    if (!start) return;
    const dx = event.clientX - start.x;
    const dy = event.clientY - start.y;
    start = null;
    if (Math.abs(dx) < SWIPE_PX || Math.abs(dx) < Math.abs(dy) * 1.5) return;
    go(dx < 0 ? next : back);
  });

  document.addEventListener("keydown", (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (event.target.closest("input, textarea, select")) return;
    if (event.key === "ArrowRight") go(next);
    if (event.key === "ArrowLeft") go(back);
  });
});
