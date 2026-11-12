---
version: 1
slug: "app-templates-home-html"
primary_target: "app/templates/home.html"
related_targets: ["app/routes/main.py","app/static/css/app.css"]
---

## Scope

The logged-out home page at `/` (#120, S5-11). Visitor mode: Persuade. Logged-in users and old `/?n=`/`/?kind=` links go to the feed, which moves to `/feed`. Inherits the Color Cut world in DESIGN.md; nothing here changes tokens.

## Audience and job

- New visitors on a phone, arriving from a shared post link or word of mouth, deciding whether this is real and safe.
- Two kinds of visitor (owner, 2026-11-11: "both, split"): people who want to help, and people who need a hand.
- The action: create an account, with the working sign-up form at the end of the page and a Sign up button in the top bar. The feed is always one link away.
- Proof: the real app pieces, each labeled Example. No invented stats, testimonials, or counts (PRODUCT.md, Evidence on Hand).

## Constraints

- Copy says "gift" and "chip in", never "donation", "donor", or "charity".
- Pay-app buttons are outlined beside a filled main action (owner, 2026-11-11).
- The plain stacked page is the default. Scroll-driven motion only under `@supports (animation-timeline: view())` and `prefers-reduced-motion: no-preference`. Works without JavaScript and at 360px with no sideways scroll.

## Direction contract

THESIS: How it works, told the way the feed moves: each step of the story cuts in sideways as its own color field, so the page teaches the app's gesture while it explains the app. It refuses the landing-page template of hero, three icon cards, and a testimonial strip.
OWN-WORLD: Always void. Want Cobalt carries the giver's path and Need Ember carries the asker's path, as full-bleed fields with the bottom scrim and white type only. League Gothic uppercase lines set huge, and Public Sans for everything else. The real app pieces sit on void beside each field: the mini ask card, outlined pay buttons, the To confirm row, state marks, the hairline meter, and the white filled primary. No gradients beyond the scrim, no glass, no shadows.
STORY: You see the two doors and know at once which one is you. Helping: pick one person, pay them in your own app (the money never touches Pay My Bill), they confirm it came through, and you get credit and a thank-you. Asking: post a want or need up to $1,000, people chip in through your app and you confirm, then say how it went and earn first shot at the top of the feed. Both paths end at the same sign-up form.
FIRST VIEWPORT: Phone: a thin void bar with the wordmark, Log in, and a white Sign up. Below it, two stacked full-bleed fields: cobalt "I want to help / CHIP IN ON SOMEONE'S BILL" and ember "I need a hand / ASK FOR UP TO $1,000", each a link into its path with "See how it works". A void strip at the foot reads "The app never holds your money." Desktop (960px and wider): the two doors sit side by side, as tall as the viewport less the bar. Signature move: the cut. Scrolling into each step wipes its field in from the right edge (clip-path inset, driven by the scroll), and its app piece slides in after it, the same way the next ask arrives on the feed.
FORM: The Color Cut scroll (surface structure round, owner pick of the dealt lead). seed:0cacb51139a21f18
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, and DESIGN.md updated with the Home page.

## Unresolved

- Per-category colors arrive with #119. Until then, the paths use the two provisional fields.
