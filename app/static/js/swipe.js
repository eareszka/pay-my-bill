// Deal through the pile: swipe left for the next ticket, right to go back, and up to open the post (#235).
// Back and Next ticket are ordinary links, so the feed works the same without this.
const ticket = document.querySelector(".deck-ticket");
const deck = document.querySelector(".deck");
const nextLink = document.querySelector(".deck-next");
const backLink = document.querySelector(".deck-back");
const panel = document.querySelector(".deck-side");
const layout = document.querySelector(".deck-layout");
const nextUnder = document.getElementById("deck-under-next");
const backUnder = document.getElementById("deck-under-back");
const calm = window.matchMedia("(prefers-reduced-motion: reduce)");
// Up opens the post, where Chip in lives.
const upLink = ticket?.querySelector(".card-title a");

const START_DRAG_PX = 8;
const COMMIT_SHARE = 0.3; // of the ticket's width
const FLICK_PX_PER_MS = 0.5;
const FLICK_MIN_PX = 30;
const FLICK_WINDOW_MS = 100;
const UP_COMMIT_PX = 80;
const UP_GIVE = 0.6; // the card follows the finger a little less than sideways
const MAX_TILT_DEG = 4;
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

const lift = (dy) => (calm.matches
  ? { opacity: 1 - Math.min(-dy / ticket.offsetHeight, 1) / 2 }
  : { transform: `translateY(${dy * UP_GIVE}px)` });

// Load and decode the neighbors' photos now. A <template> never loads its images,
// so without this a revealed card shows its bare color until the photo arrives.
const warm = new Map();
[nextUnder, backUnder].forEach((source) => {
  const photo = source?.content.querySelector(".ticket-photo");
  if (!photo) return;
  const image = new Image();
  image.className = photo.className;
  image.alt = "";
  image.src = photo.getAttribute("src");
  image.decode?.().catch(() => {});
  warm.set(source, image);
});

// Put the real neighboring ticket under this one, to be seen but not used.
const reveal = (link) => {
  if (link === underFor) return;
  under?.remove();
  under = null;
  underFor = link;
  const source = link === nextLink ? nextUnder : backUnder;
  const copy = link && source?.content.querySelector(".deck-ticket")?.cloneNode(true);
  if (!copy) return;
  const ready = warm.get(source);
  if (ready) copy.querySelector(".ticket-photo")?.replaceWith(ready);
  copy.classList.add("deck-under");
  copy.inert = true;
  copy.setAttribute("aria-hidden", "true");
  deck.append(copy);
  under = copy;
};

// Light the rail glyph for where the card is headed.
const toward = (link) => {
  if (!layout) return;
  if (link) layout.dataset.toward = link === nextLink ? "next" : "back";
  else delete layout.dataset.toward;
};

const moving = (on) => {
  deck.classList.toggle("is-moving", on);
  if (!on) {
    reveal(null);
    toward(null);
  }
};

// Play the ticket off the pile, leaving its neighbor in place, then follow the link.
const leave = (link, dx = 0) => {
  if (leaving) return;
  leaving = true;
  prefetch(link);
  moving(true);
  reveal(link);
  toward(link);
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
    duration: calm.matches ? 120 : 180,
    easing: THROW,
    fill: "forwards",
  });
  flight.finished.then(goTo, goTo);
};

// Lift the ticket off the top, then open the post.
const rise = (dy) => {
  if (leaving) return;
  leaving = true;
  const goTo = () => window.location.assign(upLink.href);
  if (!ticket.animate) {
    goTo();
    return;
  }
  const keyframes = calm.matches
    ? [lift(dy), { opacity: 0 }]
    : [lift(dy), { transform: `translateY(${-ticket.offsetHeight / 3}px)`, opacity: 0 }];
  const flight = ticket.animate(keyframes, {
    duration: calm.matches ? 120 : 180,
    easing: THROW,
    fill: "forwards",
  });
  flight.finished.then(goTo, goTo);
};

const settle = (from) => {
  ticket.style.transform = "";
  ticket.style.opacity = "";
  const back = ticket.animate
    ? ticket.animate([from, calm.matches ? { opacity: 1 } : { transform: "none" }], {
      duration: calm.matches ? 120 : 200,
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
const recentSpeed = (trail, now, axis = "x") => {
  const recent = trail.filter((point) => now - point.at <= FLICK_WINDOW_MS);
  if (recent.length < 2) return 0;
  const first = recent[0];
  const last = recent[recent.length - 1];
  return last.at > first.at ? (last[axis] - first[axis]) / (last.at - first.at) : 0;
};

const onDown = (event) => {
  if (leaving || !event.isPrimary || event.button !== 0) return;
  dragged = false;
  press = {
    id: event.pointerId,
    x: event.clientX,
    y: event.clientY,
    active: false,
    up: false,
    dx: 0,
    dy: 0,
    trail: [],
  };
};

const onMove = (event) => {
  if (!press || event.pointerId !== press.id) return;
  const raw = event.clientX - press.x;
  if (!press.active) {
    const up = event.clientY - press.y;
    if (Math.abs(raw) < START_DRAG_PX && Math.abs(up) < START_DRAG_PX) return;
    // Mostly vertical: up lifts the card toward the post; down does nothing. On phones the card
    // fills the screen (touch-action: none, since Safari has no pan-down), so no scroll is lost.
    if (Math.abs(up) > Math.abs(raw)) {
      if (up > 0 || !upLink) {
        press = null;
        return;
      }
      press.up = true;
    }
    press.active = true;
    dragged = true;
    ticket.setPointerCapture(event.pointerId);
    ticket.getAnimations().forEach((animation) => animation.cancel());
    window.getSelection()?.removeAllRanges();
    if (!press.up) moving(true);
  }
  if (press.up) {
    press.dy = Math.min(0, event.clientY - press.y);
    press.trail.push({ x: event.clientX, y: event.clientY, at: event.timeStamp });
    Object.assign(ticket.style, lift(press.dy));
    return;
  }
  const target = raw < 0 ? nextLink : backLink;
  prefetch(target);
  reveal(target);
  toward(Math.abs(raw) > START_DRAG_PX * 3 ? target : null);
  press.dx = target ? raw : raw * RESIST;
  press.trail.push({ x: event.clientX, at: event.timeStamp });
  Object.assign(ticket.style, pose(press.dx));
};

const onUp = (event) => {
  if (!press || event.pointerId !== press.id) return;
  const { active, up, dx, dy, trail } = press;
  press = null;
  if (!active) return;
  if (up) {
    const rising = recentSpeed(trail, event.timeStamp, "y") < -FLICK_PX_PER_MS && -dy > FLICK_MIN_PX;
    if (event.type === "pointerup" && (-dy > UP_COMMIT_PX || rising)) rise(dy);
    else settle(lift(dy));
    return;
  }
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
    settle(pose(dx));
  }
};

const plainClick = (event) => !(
  event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0
);

const typing = (element) => element instanceof HTMLElement
  && (element.isContentEditable || element.matches("input, select, textarea"));

if (ticket && deck && (nextLink || backLink)) {
  // Phones hand vertical moves on the card to this script, so up can open the post (#235).
  if (upLink) ticket.classList.add("swipe-up");
  ticket.addEventListener("pointerdown", onDown);
  ticket.addEventListener("pointermove", onMove);
  ticket.addEventListener("pointerup", onUp);
  ticket.addEventListener("pointercancel", onUp);
  ticket.addEventListener("dragstart", (event) => event.preventDefault());
  // A drag is never a tap on the card.
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
