// Deal through the pile: swipe left for the next ticket, right to go back.
// Back and Next ticket are ordinary links, so the feed works the same without this.
const ticket = document.querySelector(".deck-ticket");
const deck = document.querySelector(".deck");
const nextLink = document.querySelector(".deck-next");
const backLink = document.querySelector(".deck-back");
const panel = document.querySelector(".deck-side");
const nextUnder = document.getElementById("deck-under-next");
const backUnder = document.getElementById("deck-under-back");
const calm = window.matchMedia("(prefers-reduced-motion: reduce)");

const START_DRAG_PX = 8;
const COMMIT_SHARE = 0.3; // of the ticket's width
const FLICK_PX_PER_MS = 0.5;
const FLICK_MIN_PX = 30;
const FLICK_WINDOW_MS = 100;
const MAX_TILT_DEG = 6;
const RESIST = 0.25; // how far the ticket gives when there's nowhere to go
const SETTLE = "cubic-bezier(0.16, 1, 0.3, 1)";
const THROW = "cubic-bezier(0.4, 0, 1, 1)";

let leaving = false;
let press = null;
let dragged = false;
let under = null;
let underFor = null;

const tilt = (dx) => {
  const share = Math.max(-1, Math.min(1, dx / ticket.offsetWidth));
  return share * MAX_TILT_DEG;
};

const pose = (dx) => (calm.matches
  ? { opacity: 1 - Math.min(Math.abs(dx) / ticket.offsetWidth, 1) / 2 }
  : { transform: `translateX(${dx}px) rotate(${tilt(dx)}deg)` });

// Put the real neighboring ticket under this one, to be seen but not used.
const reveal = (link) => {
  if (link === underFor) return;
  under?.remove();
  under = null;
  underFor = link;
  const source = link === nextLink ? nextUnder : backUnder;
  const copy = link && source?.content.querySelector(".deck-ticket")?.cloneNode(true);
  if (!copy) return;
  copy.classList.add("deck-under");
  copy.inert = true;
  copy.setAttribute("aria-hidden", "true");
  deck.append(copy);
  under = copy;
};

const moving = (on) => {
  deck.classList.toggle("is-moving", on);
  if (!on) reveal(null);
};

// Play the ticket off the pile, leaving its neighbor in place, then follow the link.
const leave = (link, dx = 0) => {
  if (leaving) return;
  leaving = true;
  prefetch(link);
  moving(true);
  reveal(link);
  if (panel) {
    panel.inert = true;
    panel.classList.add("is-waiting");
  }
  const goTo = () => window.location.assign(link.href);
  if (!ticket.animate) {
    goTo();
    return;
  }
  const end = (link === nextLink ? -1 : 1) * (window.innerWidth + ticket.offsetWidth);
  const keyframes = calm.matches
    ? [{ opacity: pose(dx).opacity }, { opacity: 0 }]
    : [pose(dx), { transform: `translateX(${end}px) rotate(${tilt(end)}deg)` }];
  const flight = ticket.animate(keyframes, {
    duration: calm.matches ? 120 : 200,
    easing: THROW,
    fill: "forwards",
  });
  flight.finished.then(goTo, goTo);
};

const settle = (dx) => {
  ticket.style.transform = "";
  ticket.style.opacity = "";
  const back = ticket.animate
    ? ticket.animate([pose(dx), calm.matches ? { opacity: 1 } : { transform: "none" }], {
      duration: calm.matches ? 120 : 250,
      easing: SETTLE,
    })
    : null;
  if (back) back.onfinish = () => { if (!press) moving(false); };
  else moving(false);
};

const prefetched = new Set();
const prefetch = (link) => {
  if (!link || prefetched.has(link.href)) return;
  prefetched.add(link.href);
  const hint = document.createElement("link");
  hint.rel = "prefetch";
  hint.href = link.href;
  document.head.append(hint);
};

// How fast the pointer was going just before it let go, so a pause counts as no flick.
const recentSpeed = (trail, now) => {
  const recent = trail.filter((point) => now - point.at <= FLICK_WINDOW_MS);
  if (recent.length < 2) return 0;
  const first = recent[0];
  const last = recent[recent.length - 1];
  return last.at > first.at ? (last.x - first.x) / (last.at - first.at) : 0;
};

const onDown = (event) => {
  if (leaving || !event.isPrimary || event.button !== 0) return;
  dragged = false;
  press = {
    id: event.pointerId,
    x: event.clientX,
    y: event.clientY,
    active: false,
    dx: 0,
    trail: [],
  };
};

const onMove = (event) => {
  if (!press || event.pointerId !== press.id) return;
  const raw = event.clientX - press.x;
  if (!press.active) {
    const up = event.clientY - press.y;
    if (Math.abs(raw) < START_DRAG_PX && Math.abs(up) < START_DRAG_PX) return;
    // Mostly vertical: this is a scroll, so leave it alone.
    if (Math.abs(up) > Math.abs(raw)) {
      press = null;
      return;
    }
    press.active = true;
    dragged = true;
    ticket.setPointerCapture(event.pointerId);
    ticket.getAnimations().forEach((animation) => animation.cancel());
    window.getSelection()?.removeAllRanges();
    moving(true);
  }
  const target = raw < 0 ? nextLink : backLink;
  prefetch(target);
  reveal(target);
  press.dx = target ? raw : raw * RESIST;
  press.trail.push({ x: event.clientX, at: event.timeStamp });
  Object.assign(ticket.style, pose(press.dx));
};

const onUp = (event) => {
  if (!press || event.pointerId !== press.id) return;
  const { active, dx, trail } = press;
  press = null;
  if (!active) return;
  const target = dx < 0 ? nextLink : backLink;
  const speed = recentSpeed(trail, event.timeStamp);
  const flicked = Math.abs(speed) > FLICK_PX_PER_MS
    && Math.abs(dx) > FLICK_MIN_PX && Math.sign(speed) === Math.sign(dx);
  const far = Math.abs(dx) > ticket.offsetWidth * COMMIT_SHARE;
  if (event.type === "pointerup" && target && (far || flicked)) {
    ticket.style.transform = "";
    ticket.style.opacity = "";
    leave(target, dx);
  } else {
    settle(dx);
  }
};

const plainClick = (event) => !(
  event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0
);

const typing = (element) => element instanceof HTMLElement
  && (element.isContentEditable || element.matches("input, select, textarea"));

if (ticket && deck && (nextLink || backLink)) {
  ticket.addEventListener("pointerdown", onDown);
  ticket.addEventListener("pointermove", onMove);
  ticket.addEventListener("pointerup", onUp);
  ticket.addEventListener("pointercancel", onUp);
  ticket.addEventListener("dragstart", (event) => event.preventDefault());
  // A drag is never a tap on the title or the Chip in tab.
  ticket.addEventListener("click", (event) => {
    if (!dragged) return;
    dragged = false;
    event.preventDefault();
    event.stopPropagation();
  }, true);

  [nextLink, backLink].forEach((link) => {
    link?.addEventListener("click", (event) => {
      if (!plainClick(event)) return;
      event.preventDefault();
      leave(link);
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.repeat || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (typing(event.target)) return;
    const link = { ArrowRight: nextLink, ArrowLeft: backLink }[event.key];
    if (link) leave(link);
  });

  // Coming back with the browser's Back button can restore the ticket mid-flight.
  window.addEventListener("pageshow", (event) => {
    if (!event.persisted) return;
    leaving = false;
    press = null;
    ticket.getAnimations().forEach((animation) => animation.cancel());
    moving(false);
    if (panel) {
      panel.inert = false;
      panel.classList.remove("is-waiting");
    }
  });
}
