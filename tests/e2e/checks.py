"""Design checks run on every page the e2e tests visit (#207).

Each check returns a list of findings, `{"check": ..., "detail": ...}`, measured in the
real browser rather than read from the templates.
"""

from typing import Any, Protocol

from playwright.sync_api import Page

Finding = dict[str, Any]

# WCAG 2.5.5 and Apple's HIG both ask for 44pt touch targets.
MIN_TAP = 44
# How many Tab presses the focus check walks through.
FOCUS_STOPS = 15
# How far outside a control its focus ring may be drawn, and how long it may take to appear.
FOCUS_PAD = 12
FOCUS_SETTLE_MS = 250

OVERFLOW_JS = """
() => {
  const doc = document.documentElement;
  if (doc.scrollWidth <= doc.clientWidth + 1) return [];
  const wide = [...document.querySelectorAll('body *')]
    .filter(el => el.getBoundingClientRect().right > doc.clientWidth + 1)
    .filter(el => getComputedStyle(el).position !== 'fixed')
    .slice(0, 5)
    .map(el => el.tagName.toLowerCase() + (el.className ? '.' + [...el.classList].join('.') : ''));
  return [`page is ${doc.scrollWidth}px wide in a ${doc.clientWidth}px viewport; widest: ${wide.join(', ')}`];
}
"""

TAP_JS = """
(min) => {
  const out = [];
  const visible = el => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.visibility !== 'hidden' && s.display !== 'none' && r.width > 0 && r.height > 0
      && !el.closest('[hidden], .sr-only, [aria-hidden=true]');
  };
  // WCAG 2.5.8 exempts links inside a sentence; only standalone controls must be big.
  const inline = el => {
    const block = el.closest('p, li, small, label, td, dd');
    return el.tagName === 'A' && block && block.textContent.trim().length > el.textContent.trim().length + 2;
  };
  const sel = 'a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button]';
  for (const el of document.querySelectorAll(sel)) {
    if (!visible(el) || inline(el)) continue;
    let r = el.getBoundingClientRect();
    // A checkbox or radio counts its label, which is what the finger actually hits.
    if (el.type === 'checkbox' || el.type === 'radio') {
      const label = el.closest('label') || (el.id && document.querySelector(`label[for="${el.id}"]`));
      if (label) r = label.getBoundingClientRect();
    }
    if (r.width < min || r.height < min) {
      const name = (el.getAttribute('aria-label') || el.textContent || el.name || el.id || '').trim().replace(/\\s+/g, ' ').slice(0, 40);
      out.push(`<${el.tagName.toLowerCase()}> "${name}" is ${Math.round(r.width)}x${Math.round(r.height)}px`);
    }
  }
  return out;
}
"""

FOCUS_JS = r"""
(pad) => {
  const el = document.activeElement;
  if (!el || el === document.body) return null;
  const r = el.getBoundingClientRect();
  const name = (el.getAttribute('aria-label') || el.textContent || el.name || el.id || '').trim().replace(/\s+/g, ' ').slice(0, 40);
  // The area a ring could show in: the element plus a margin, kept inside the viewport.
  const x = Math.max(0, r.left - pad), y = Math.max(0, r.top - pad);
  const clip = {x, y,
    width: Math.min(innerWidth, r.right + pad) - x,
    height: Math.min(innerHeight, r.bottom + pad) - y};
  return {name: `<${el.tagName.toLowerCase()}> "${name}"`, clip};
}
"""

CONTRAST_JS = """
() => {
  const parse = c => {
    const m = c.match(/rgba?\\(([^)]+)\\)/);
    if (!m) return null;
    const [r, g, b, a = 1] = m[1].split(/[ ,\\/]+/).filter(Boolean).map(Number);
    return {r, g, b, a};
  };
  const lum = ({r, g, b}) => {
    const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  // The first solid background behind an element; null if a photo or gradient is in the way.
  const backdrop = el => {
    for (let n = el; n; n = n.parentElement) {
      const s = getComputedStyle(n);
      if (s.backgroundImage !== 'none') return null;
      const c = parse(s.backgroundColor);
      if (c && c.a >= 0.95) return c;
    }
    return {r: 255, g: 255, b: 255, a: 1};
  };
  const out = new Set();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let t = walker.nextNode(); t; t = walker.nextNode()) {
    const text = t.textContent.trim();
    const el = t.parentElement;
    if (!text || !el || el.closest('[hidden], .sr-only, [aria-hidden=true], script, style')) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const s = getComputedStyle(el);
    if (s.visibility === 'hidden' || parseFloat(s.opacity) === 0) continue;
    const fg = parse(s.color), bg = backdrop(el);
    if (!fg || !bg) continue;
    const [hi, lo] = [lum(fg), lum(bg)].sort((a, b) => b - a);
    const ratio = (hi + 0.05) / (lo + 0.05);
    const size = parseFloat(s.fontSize), bold = parseInt(s.fontWeight) >= 700;
    const need = size >= 24 || (bold && size >= 18.66) ? 3 : 4.5;
    if (ratio < need) out.add(`"${text.slice(0, 40)}" is ${ratio.toFixed(2)}:1 (needs ${need}:1), ${s.color} on rgb(${bg.r}, ${bg.g}, ${bg.b})`);
  }
  return [...out].slice(0, 10);
}
"""

MOTION_JS = """
() => document.getAnimations()
  .map(a => ({name: a.animationName || a.transitionProperty || 'animation',
              ms: Number(a.effect?.getComputedTiming().duration) || 0,
              target: a.effect?.target?.className || ''}))
  .filter(a => a.ms > 250)
  .map(a => `${a.name} on .${String(a.target).split(' ').join('.')} runs ${Math.round(a.ms)}ms`)
"""


def finding(check: str, details: list[str]) -> list[Finding]:
    return [{"check": check, "detail": d} for d in details]


def overflow(page: Page) -> list[Finding]:
    return finding("horizontal-overflow", page.evaluate(OVERFLOW_JS))


def tap_targets(page: Page) -> list[Finding]:
    return finding("tap-target", page.evaluate(TAP_JS, MIN_TAP))


def contrast(page: Page) -> list[Finding]:
    return finding("contrast", page.evaluate(CONTRAST_JS))


def focus_visible(page: Page) -> list[Finding]:
    """Tab through the first controls and report any whose focus changes nothing on screen.

    Rings can be drawn on the element, a pseudo-element, or a child (#205's card ring is a
    ::after overlay; the deck's Next ring is on its icon), so compare pixels, not styles.
    """
    missing: list[str] = []
    page.evaluate("() => document.activeElement && document.activeElement.blur()")
    for _ in range(FOCUS_STOPS):
        page.keyboard.press("Tab")
        page.wait_for_timeout(FOCUS_SETTLE_MS)
        state = page.evaluate(FOCUS_JS, FOCUS_PAD)
        if (
            not state
            or state["name"] in missing
            or min(state["clip"]["width"], state["clip"]["height"]) <= 0
        ):
            continue
        focused = page.screenshot(clip=state["clip"])
        page.evaluate(
            "() => { window.__e2eFocus = document.activeElement; window.__e2eFocus.blur(); }"
        )
        page.wait_for_timeout(FOCUS_SETTLE_MS)
        blurred = page.screenshot(clip=state["clip"])
        # Put focus back so the next Tab carries on from here.
        page.evaluate("() => window.__e2eFocus.focus()")
        if focused == blurred:
            missing.append(state["name"])
    return finding("focus-visible", [f"{name} has no visible focus ring" for name in missing])


def long_motion(page: Page) -> list[Finding]:
    """With reduced motion on, nothing should still be animating for long."""
    return finding("reduced-motion", page.evaluate(MOTION_JS))


def run_all(page: Page, *, mobile: bool, focus: bool = True) -> list[Finding]:
    found = overflow(page) + contrast(page)
    if mobile:
        found += tap_targets(page)
    elif focus:
        # Keyboard focus is a desktop concern; Tab moves the page, so it runs last.
        found += focus_visible(page)
    return found


class HasFindings(Protocol):
    device: str
    findings: list[Finding]


def assert_clean(ui: HasFindings) -> None:
    """Fail with a readable list of everything the design checks found."""
    lines = [f"[{f['check']}] {f['page']} ({f['step']}): {f['detail']}" for f in ui.findings]
    assert not lines, f"{len(lines)} design findings on {ui.device}:\n" + "\n".join(lines)
