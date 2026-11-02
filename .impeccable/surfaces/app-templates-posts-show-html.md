---
version: 1
slug: "app-templates-posts-show-html"
primary_target: "app/templates/posts/show.html"
related_targets: ["app/templates/profile/show.html"]
---

## Scope

Sprint 4 additions to the post page: the close date, Close post with an inline confirm, the results update prompt, form, and display, and kudos and reactions. Also the follow-through stat on the public profile. Visitor mode: Operate. Extension of the incumbent visual world in app/static/css/app.css; no DESIGN.md exists yet.

## Audience and task

- Donors (primary user): find out what their gift did, and respond in one tap.
- Posters: close a post when done, and report back before the deadline with no fuss. Usually arriving from an email reminder.
- States: open post, close confirm, closed or funded, update owed, overdue, invalid note, update posted, deleted post that still owes, reactions as a visitor, a member, a donor, and an admin; light and dark themes.

## Constraints

- Owner choices (2026-11-02): keep the current look; updates live on the post page; closing asks once inline, with no popup; 👍 and 🤨 are the owner's own symbols; 🤨 counts are visible only to admins.
- Copy says "gift" or "chip in", never "donation" or "charity". Receipts are never required, and the form warns against sharing account numbers or medical details (T14).
- Works without JavaScript; 360px phones without horizontal scroll.

## Direction contract

THESIS: The post page gets a second act. Once a post closes, the page stops asking and starts answering, so the results update takes the place chip-in held; refuse any celebration that outshouts the poster's own words.
OWN-WORLD: Inherited: system sans, near-white ground, white cards with 12px radius and a 1px border, green accent for primary actions, tinted notices, the error red only for destructive actions.
STORY: A donor opens a closed post, reads what happened in the poster's words, and taps Kudos. A poster sees what's owed and by when, writes a few lines, and posts.
FIRST VIEWPORT: Unchanged through the story. The update section sits where chip-in sat. Poster controls stay last, in the existing danger zone.
FORM: Extension of the incumbent product shell (position 1 of 1). seed: none (extension of the incumbent world; no roll)
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review and the verdict.
