---
version: 1
slug: "app-templates-gifts-index-html"
primary_target: "app/templates/gifts/index.html"
related_targets: ["app/templates/base.html"]
---

## Scope

`/gifts` (app/templates/gifts/index.html) plus the Gifts count badge in the top bar (app/templates/base.html). Visitor mode: Operate. Extension of the incumbent visual world in app/static/css/app.css; no DESIGN.md exists yet.

## Audience and task

- Posters: confirm or dispute gifts donors say they sent, after checking their payment app. Infrequent, a few times per post, usually arriving from the email notice or the top-bar badge.
- Donors (primary user): see the gifts they recorded and whether each was confirmed.
- States: gifts waiting (count shown), dispute confirmation for one gift, no gifts yet, long usernames in the top bar, light and dark themes.

## Constraints

- Owner choices (2026-10-30): one /gifts page with "To confirm" and "My gifts"; a badge with the waiting count; disputing asks once inline, with no popup.
- Keep the existing colors, themes, layout, and wording. Copy says "gift", never "donation" or "charity".
- Works without JavaScript; 360px phones without horizontal scroll.

## Direction contract

THESIS: A quiet ledger of honest credit. The task is judging whether money arrived, so the amount leads each item and the decision sits right under it; refuse the dashboard-of-stats arrangement.
OWN-WORLD: Inherited: system sans, near-white ground, white cards with 12px radius and a 1px border, green accent for primary actions, the error red only for the destructive dispute, uppercase pill chips for status.
STORY: The poster sees how much, from whom, through which app, and for which post, checks the app, and confirms. The donor sees each gift's status in plain words: Waiting, Confirmed, Not received.
FIRST VIEWPORT: Title, then "To confirm N" with the check-your-app hint, then a card per gift: a 1.5rem amount, "via App from donor", "for post · date", then Confirm and "Didn't get it" side by side. "My gifts" follows as one divided list: amount, recipient, and status chip, with the post on a second line.
FORM: Extension of the incumbent product shell (position 1 of 1). seed: none (extension of the incumbent world; no roll)
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
