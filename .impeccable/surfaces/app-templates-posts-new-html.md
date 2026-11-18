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

To be set by ui (Impeccable).
