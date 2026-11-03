---
version: 1
slug: "app-templates-base-html"
primary_target: "app/templates/base.html"
related_targets: ["app/templates/index.html","app/templates/posts/show.html","app/templates/gifts/index.html","app/templates/leaders/index.html","app/templates/profile/show.html"]
---

## Scope

The whole app shell and every page: feed, post page, gifts, leaders, profile, sign up and log in, forms, and rules. Visitor mode: Operate. Replaces the Seed Rack world.

## Audience and task

- Donors (primary user): on a phone, see who needs a hand, trust it, and chip in within a few taps.
- Posters: ask plainly, confirm gifts, and report back to earn the top of the board.
- States: top ticket or none, post with a photo or none, open, closed, funded, update owed or overdue, gift waiting, confirmed, not received, or expired, form errors, empty lists, long usernames, light and dark themes.

## Constraints

- Owner brief (2026-11-03): simple and trustworthy, with personality. It must never feel like a sad charity page, a bank or finance app, a game or casino, a generic startup, or a typical scroll app. The rack was too cluttered and gave each post too little visibility.
- Owner: a bulletin board with no thumbtacks. Each post is just a page or ticket. The large top ticket rewards posters who follow through (ADR 0013).
- Poster photos are optional and come in a later story; a ticket with no photo must look complete.
- Copy says "gift" or "chip in", never "donation" or "charity".
- Works without JavaScript; 360px phones without horizontal scroll; light and dark.

## Direction contract

THESIS: The community board at the door. One ticket gets the top of the board because its poster follows through, and the rest sit plainly beneath it. It refuses the endless feed and the crowdfunding plea.
OWN-WORLD: Flat cork ground and a dark wood top bar. Square white paper tickets with a soft shadow, light blue for wants. Leaf green only for primary actions, including the tear-off tab with its dashed edge. Tomato only for errors and destructive actions. Bitter extra-bold for titles, Public Sans for everything else. No pins, no plant art, no faked cork texture.
STORY: The visitor sees one person up close, then others nearby, and chips in. Everything sits on a ticket, so text never rests on a busy surface. After a post closes, the poster's own words take over.
FIRST VIEWPORT: Wood top bar with brand left and Post, Gifts, Leaders, and user right. Underlined All, Needs, Wants tabs on cork. One full-width ticket: a large photo when there is one, a large Bitter title, who and where, a short story line, the amount, and a full-width green Chip in tab. Beneath it, two columns of small tickets with title, who and where, and amount. Signature move: the tear-off Chip in tab, plus the ten-mark row, which fills once on the post page.
FORM: Top of the Board, position 3 of 6 on the grounded list. seed:1ead20c5faed4470
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
