---
version: 1
slug: "app-templates-home-html"
primary_target: "app/templates/home.html"
related_targets: ["app/templates/how/story.html","app/routes/main.py","app/static/css/app.css","app/static/js/how.js"]
---

## Scope

The logged-out home page at `/` and the two how-it-works stories at `/how/help` and `/how/ask` (#120, S5-11). Visitor mode: Persuade. Logged-in users and old `/?n=`/`/?kind=` links go to the feed at `/feed`. Inherits the Color Cut world in DESIGN.md; nothing here changes tokens.

## Audience and job

- New visitors on a phone, arriving from a shared post link or word of mouth, deciding whether this is real and safe.
- Two kinds of visitor (owner, 2026-11-11: "both, split"): people who want to help, and people who need a hand.
- The action: create an account. Each story ends on Sign up (to `/signup`) or the other story. The feed is always one link away in the nav.
- Proof: the real app pieces, each labeled Example. No invented stats, testimonials, or counts (PRODUCT.md, Evidence on Hand).

## Constraints

- Owner, 2026-11-11 (second pass): the first page is just the two options; each opens its own story; each story ends on Sign up or the other story; no single long scrolling page; stories use animation; Impeccable makes the design choices.
- Copy says "gift" and "chip in", never "donation", "donor", or "charity".
- Every step is its own server-rendered URL, so Back, history, links, and JavaScript-off all work. Motion is cross-document View Transitions under `prefers-reduced-motion: no-preference`; without support it is plain navigation.
- Works at 360px with no sideways scroll.

## Direction contract

THESIS: The door opens. You pick which one is you, and that door becomes the whole screen; the story plays inside it one step at a time, cutting in the way the feed moves. It refuses the long landing page of hero, icon cards, and testimonials.
OWN-WORLD: Always void. Want Cobalt is the helping field, Need Ember the asking field, each with the bottom scrim and white type only. League Gothic uppercase lines set huge; Public Sans for everything else. The real app pieces sit inside the field: mini ask card, pay buttons, To confirm rows, state marks, hairline meter, white filled primary. No gradients beyond the scrim, no glass, no shadows.
STORY: Helping: pick one person, pay them in your own app (the money never touches Pay My Bill), they confirm it came through, you get credit and a thank-you. Asking: ask for up to $1,000, people chip in through your app and you confirm, say how it went. Each ends on Sign up, or the other door.
FIRST VIEWPORT: Home: the thin void bar with the wordmark and a white Sign up, then two full-bleed doors, cobalt "I want to help" over ember "I need a hand" (side by side from 960px), each "See how it works", and a void line "Pay My Bill never holds your money." Story step: one field fills the screen with segmented progress bars (the field's color names the door; no label above the heading, per the eyebrow ban), the huge step line, one sentence, the Example piece, and Back / n of N / Next; the other door waits docked as a strip at the foot.
FORM: The Door Opens (surface structure round, owner pick of the dealt lead). seed:b7e4647302ecad91. Signature move: the tapped door morphs into the story field while the other door shrinks into the docked strip; each step's content wipes in from the right (from the left going back); taking the docked strip swaps the two.
DOOR PHOTOS (owner, 2026-11-11, Impeccable round pick "Tinted Mosaic"): each door carries photos from real posts, open asks behind help and funded asks behind asking, grayscale and multiplied into the door's color, three across on phones and three by two from 960px, fading to the solid field before the words. Only verified, unbanned, never-reported accounts; six or none.
STEP PHOTOS (owner, 2026-11-11, Impeccable round pick "Photo Band"): every story step carries three of its door's photos (help: open asks, ask: funded) across the top of the field, tinted like the doors and fading to solid field by half height behind the headline; steps alternate between the two sets of three; no photos when the door has none.
SIGN-UP HANDOFF (owner, 2026-11-12, Impeccable round pick "Button Becomes the Form"): the last step's white Sign up links to `/signup?from=<story>`; the sign-up page is a void stage page for everyone, "Join in" in League Gothic, the form in a white-edged dark card. View Transitions: the Sign up button (join-card) grows into the card, the step words leave as the page's content cuts in (how-step), and the story field (field-help/field-ask) sinks into a full-width strip in the story's color, sticky at the foot, "Back to how helping/asking works". Plain `/signup` has no strip.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, and DESIGN.md updated.

## Unresolved

- Per-category colors arrive with #119. Until then, the stories use the two provisional fields.
