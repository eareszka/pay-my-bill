// A row of pills (the tab bar, the feed filter, Leaders, You) slides its current pill over from the tab
// you just left, Instagram-style (#227). Labels never move. Without this, the pill simply lands.
// Loaded in <head> without defer, so pagereveal is heard before the first frame.
// A block keeps these names out of the global scope the other classic scripts share.
{
  const KEY = "pill-from";
  const ROW = "nav.tabs, .topbar > nav";
  const CURRENT = 'a[aria-current="page"]';

  // The link's edges as distances from its row's edges, so they carry across pages.
  const edges = (row, link) => {
    const r = row.getBoundingClientRect();
    const l = link.getBoundingClientRect();
    return { left: l.left - r.left, right: r.right - l.right };
  };

  document.addEventListener("click", (event) => {
    const link = event.target.closest?.("a[href]");
    const row = link?.closest(ROW);
    const current = row?.querySelector(CURRENT);
    if (!current || current === link) return;
    try {
      sessionStorage.setItem(KEY, JSON.stringify({ row: row.getAttribute("aria-label"), at: Date.now(), ...edges(row, current) }));
    } catch {}
  });

  const slide = () => {
    let from;
    try {
      from = JSON.parse(sessionStorage.getItem(KEY));
    } catch { return true; }
    if (!from || Date.now() - from.at > 3000 || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return true;
    const row = [...document.querySelectorAll(ROW)].find((each) => each.getAttribute("aria-label") === from.row);
    const link = row?.querySelector(CURRENT);
    if (!link) return false;
    try { sessionStorage.removeItem(KEY); } catch {}
    const to = edges(row, link);
    if (!link.animate || (from.left === to.left && from.right === to.right)) return true;
    const pill = getComputedStyle(link, "::before");
    const left = parseFloat(pill.left);
    const right = parseFloat(pill.right);
    const timing = { duration: 220, easing: "cubic-bezier(0.16, 1, 0.3, 1)" };
    link.animate(
      [{ left: `${left + from.left - to.left}px`, right: `${right + from.right - to.right}px` }, { left: `${left}px`, right: `${right}px` }],
      { ...timing, pseudoElement: "::before" },
    );
    // The label turns white as the pill arrives, not before.
    const other = row.querySelector(`a:not(${CURRENT})`);
    if (other) link.animate([{ color: getComputedStyle(other).color }, {}], timing);
    return true;
  };

  const reveal = () => {
    if (!slide() && document.readyState === "loading") document.addEventListener("DOMContentLoaded", slide, { once: true });
  };
  if ("onpagereveal" in window) window.addEventListener("pagereveal", reveal);
  else document.addEventListener("DOMContentLoaded", slide, { once: true });
}
