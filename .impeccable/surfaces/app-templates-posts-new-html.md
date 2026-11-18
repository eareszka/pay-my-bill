---
version: 1
slug: "app-templates-posts-new-html"
primary_target: "app/templates/posts/new.html"
related_targets: ["app/static/js/steps.js","app/static/css/app.css"]
---

## Scope

The new-post page at `/posts/new` (#275), asked one question per screen. Inherits DESIGN.md.

## Constraints

- Owner, 2026-11-18: make it feel like Hinge or Bumble onboarding. The owner's reference screenshots show a thin progress bar at the top, a big bold question, a one-line grey hint, full-width option rows with a check box on the right (need or want), emoji pills that wrap (category), a round dark → button at the bottom right, and Skip at the bottom left on optional steps.
- Same fields as before, with no dating-only screens. Steps: need or want → category → title → story → goal → photo (optional) → rules (first post only). The last step's → is the Post button.
- main's working version: `steps.js` shows one `[data-step]` at a time, sets `form[data-steps=on]`, moves the progress bar, and auto-advances after a single-choice pick (250 ms). A server error opens on the first step with an `.error`. Without JS the page is one long form. Keep that.
- The form, validation, CSRF, moderation, the open-post limit and `edit.html` are unchanged.

## Direction contract

Mode: Operate. Yearnly's world, with onboarding pacing (ui, 2026-11-18).

- The page title hides while the steps run; the progress bar (4px, mark-empty track, Dollar Green fill, 320ms) leads the screen.
- The question is League Gothic uppercase at the h1 size (owner's pick "Yearnly display", over Hinge's bold sentence case), with the hint under it in muted 1rem. A text step's field label is for screen readers only, since the question names it.
- Need or want: full-width 64px hairline rows, the word in 1.25rem 700 on the left and a 26px rounded box on the right that fills Dollar Green and ticks.
- Category: 48px emoji pills that wrap, as hidden real radios (the tip row's pattern), filling Dollar Green with white text.
- The foot: a 60px Press Green → circle at the right (Deep on hover), a 52px outlined ← circle and Skip at the left, and on the last step a "Post →" primary pill in place of the →. On a phone the form fills the space between the bars and the footer hides, so the → is in thumb reach and nothing scrolls.
- Motion: the step slides 32px in from the side you're heading to and fades in over 300ms on `--ease-out`; a ticked box pops in. Reduced motion cuts.
