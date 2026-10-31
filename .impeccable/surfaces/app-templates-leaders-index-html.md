---
version: 1
slug: "app-templates-leaders-index-html"
primary_target: "app/templates/leaders/index.html"
related_targets: ["app/templates/base.html"]
---

## Scope

`/leaders` (app/templates/leaders/index.html) and the top-bar change: Leaders is added, and Log out moves to the profile edit page. Visitor mode: Operate. Extension of the incumbent visual world in app/static/css/app.css.

## Audience and task

- Donors (primary): see where they rank by people helped, this week and all time, globally and in their own state and city. Opened casually, a few times a week.
- Logged-out visitors see the global board only.
- States: a full board, an empty board (early beta, a new week), the viewer in the top 20 (highlighted), the viewer outside the top 20 (their row below the list), and a viewer with no region (Global only).

## Constraints

- Owner choices (2026-10-31): profile plus Leaders page; ranking by people helped, never dollars (ADR 0009); Log out moves to the profile page so Leaders fits the top bar at 360px.
- Keep the existing colors, themes, layout, and wording. Use the existing pill tabs for scope and period.

## Direction contract

THESIS: A plain ranked ledger of people helped. The number that matters is people, never money, so rows carry rank, name, and people only; refuse podiums, trophies, and dollar totals.
OWN-WORLD: Inherited: system sans, near-white ground, pill tabs (accent when current), one bordered list with dividers like "My gifts", tabular numerals, accent only for the viewer's own row and the current tab.
STORY: A donor sees how many people the top helpers reached, finds themselves, and wants to help one more person.
FIRST VIEWPORT: "Leaders" title, then one hint line stating the rule ("Ranked by how many different people each donor has helped. Only confirmed gifts count."). It's the only on-page statement that the board counts people, not dollars (ADR 0009) or unconfirmed claims (ADR 0004). Then a scope tab row (Global, state, city), a period tab row (This week, All time), then the ranked list: rank right-aligned in a narrow column, username, and "N people" right-aligned. The viewer's row is marked. Below the list: "You: #31 · 4 people" when the viewer is outside the top 20.
FORM: Extension of the incumbent product shell (position 1 of 1). seed: none (extension of the incumbent world; no roll)
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
