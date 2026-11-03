---
version: 1
slug: "app-templates-base-html"
primary_target: "app/templates/base.html"
related_targets: ["app/templates/index.html","app/templates/posts/show.html","app/templates/gifts/index.html","app/templates/leaders/index.html","app/templates/profile/show.html"]
---

## Scope

The whole app shell and every page: feed, post page, gifts, leaders, profile, sign up and log in, forms, and rules. Visitor mode: Operate. Replaces the earlier visual world; no earlier look carries over.

## Audience and task

- Donors (primary user): on a phone, see what someone needs, trust it, and chip in within a few taps.
- Posters: ask plainly, confirm gifts, and report back.
- States: post with a photo or none, open, closed, funded, update owed or overdue, gift waiting, confirmed, not received, or expired, form errors, empty lists, long usernames, light and dark themes.

## Constraints

- Owner brief (2026-11-03): simple and trustworthy, with personality. It must never feel like a sad charity page, a bank or finance app, a game or casino, or a generic startup. The owner chose this look after asking for photos on posts.
- Poster photos are optional and come in a later story; a post with no photo must look complete, never like a missing image.
- Copy says "gift" or "chip in", never "donation" or "charity". Keep existing wording and behavior.
- Works without JavaScript; 360px phones without horizontal scroll; light and dark.

## Direction contract

THESIS: A garden-aisle seed packet shows what you're helping grow and states plainly what it takes. Each post is that packet: picture or flat colour band, plain facts, one action. It refuses the crowdfunding plea and the gamified dashboard.
OWN-WORLD: Leaf green shell, pale green ground, white panels with 6px corners, flat colour bands: leaf for needs, deep teal for wants. Marigold only on what can be pressed as a primary action; tomato only for errors and destructive actions. Bitter extra-bold for titles, Public Sans for everything else, because plain zeros read better on money than Atkinson's slashed ones. No plant art anywhere.
STORY: The visitor sees real asks, reads who and where, sees how far along each is, and chips in. After a post closes, the poster's own words take over. Hierarchy comes from size, state uses one consistent mark, nothing is labelled twice, and money lines up tight wherever it's listed.
FIRST VIEWPORT: Leaf top bar with brand left and Post, Gifts, Leaders, and user right. Underlined All, Needs, Wants tabs below. Then full-width panels: a colour band with a large title (a photo with the title beneath, later), who and where, the growing row, then amount left and a marigold Chip in right. Signature move: progress is a growing row of ten marks that fills left to right once on the post page, where it takes full colour. Reduced motion shows it filled at once.
FORM: Seed Packet, position 6 of 7 on the grounded list. seed:e47b0b2c1a7029fc
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
