---
version: 1
slug: "app-templates-auth-signup-html"
primary_target: "app/templates/auth/signup.html"
related_targets: ["app/routes/auth.py","app/static/css/app.css"]
---

## Scope

The sign-up page at `/signup` (#120 handoff). Visitor mode: Operate inside the Color Cut stage. Inherits DESIGN.md; nothing here changes tokens. Strategy for the stories that lead here lives in `.impeccable/surfaces/app-templates-home-html.md` (SIGN-UP HANDOFF).

## Constraints

- The form, validation, CSRF, sign-up rate limit, 18+ attestation, and Terms/Privacy links are unchanged (`app/routes/auth.py` `signup`).
- Owner, 2026-11-12: Impeccable round pick "Button Becomes the Form". The page is a void stage page for everyone; arrivals from a story (`?from=help|ask`) get a full-width strip in that story's color, sticky at the foot, linking back to its last step. Any other `from` is ignored.

## Direction contract

THESIS: Signing up is the last move of the story, not a new page: the button you tapped becomes the form.
OWN-WORLD: Void stage, white ink, League Gothic "Join in", Public Sans for the rest; the form in a dark surface card with a 1.5px white edge and 16px corners; the story's field color only as the strip at the foot.
FIRST VIEWPORT: Bar, "Join in", one sentence, the form card with the white Sign up, "Already have an account? Log in", and (from a story) the color strip "Back to how helping/asking works".
FORM: Button Becomes the Form (owner pick, code-led; a local-extension round whose three options were authored, not dealt, so it has no roll of its own; the parent surface roll is seed:b7e4647302ecad91). View Transitions: join-card (story Sign up button to the form card), how-step (story words out, page content in), field-help/field-ask (story field sinks into the strip).
FINISH: finish review and DESIGN.md updated.
