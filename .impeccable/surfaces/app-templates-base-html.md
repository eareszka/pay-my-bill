---
version: 1
slug: "app-templates-base-html"
primary_target: "app/templates/base.html"
related_targets: ["app/templates/index.html","app/templates/posts/show.html","app/templates/gifts/index.html","app/templates/leaders/index.html","app/templates/profile/show.html"]
---

## Scope

The whole app shell and every page: feed, post page, gifts, leaders, profile, sign up and log in, forms, rules, admin, and errors. Visitor mode: Operate. Replaces the cork-board world (owner, 2026-11-09). The logged-out home page has its own Persuade brief.

## Audience and task

- Donors (primary user): on a phone, see one person's ask at a time, swipe on or back, push a kind down, and chip in within a few taps.
- Posters: ask plainly, confirm gifts, and report back to earn the top of the stack.
- States: an ask or none, open, closed, funded, update owed or overdue, gift waiting, confirmed, not received, or expired, mid-drag in each direction, show-less undo, form errors, empty lists, long titles and usernames, light and dark on non-feed pages.

## Constraints

- Owner (2026-11-09): must not look AI-made, and must be coherent and simple. It's modeled on dating-app swiping, but you can go back. Motion is fast, readable, and stylized.
- Gestures are pinned by the owner: left = next, right = back, down = show less, plus visible buttons for each. No vertical-snap feed.
- Photos are optional (#122, ADR 0015). With a photo, the ask is the photo under a deeper scrim; without one, it is a color field. Category colors arrive with #119; until then, Need and Want get one color each.
- Feed and post stage are always dark. Forms, Gifts, Leaders, profile, and admin follow the system theme in the same type and accents.
- Copy says "gift" or "chip in", never "donation" or "charity". Works without JavaScript, and at 360px without horizontal scroll.

## Direction contract

THESIS: One person's ask owns the whole screen. You flick through people the way you flick through a feed, but sideways, with a way back, and every ask is one tap from a real gift. It refuses the crowdfunding page, the card grid, and the endless vertical scroll.
OWN-WORLD: A void-black shell (#0a0a0a, ink #121316, slate #1e2026, fog #5a6472) with pure white glyphs and type as the only interface ink. Each ask is a full-bleed, saturated category field that holds white text at 4.5:1 or better, under a soft bottom scrim. League Gothic for titles, set huge and tall. Public Sans for everything else. A white filled Chip in is the one primary action, outline buttons are secondary, and the rail glyphs are thin white line icons that fill when engaged. Tomato appears only for errors. No gradients beyond the scrim, no glass, no glow.
STORY: The visitor sees one person's ask, huge, in its category's color. They chip in from the rail or the panel, flick to the next, flick back, or push that category down. After a post closes, the poster's thank-you takes over the stage.
FIRST VIEWPORT: Phone: a thin top strip with the brand at left and All, Needs, Wants centered as white text tabs. The ask's color field fills the screen. The title sits mid-left in League Gothic at about 64px. Bottom left holds who · where · Need/Want, the 140-character story, and "$45 of $180" with a hairline progress bar. The right rail holds Chip in ($, filled white), Show less (↓), Back (↶), and Share, each labeled. A bottom nav bar on void reads Feed, Post, Gifts, Leaders, You. Desktop (960px and wider): a centered 9:16 stage of about 470×836 holding the same composition and rail, with the Chip in panel on void beside it and the top nav across. Signature move: the color cut. As you drag, the next or previous ask's field is already there underneath, the target rail glyph lights, and on release the stage snaps in 180ms with no partial position. A down-drag drops the card and fills the Show less glyph.
FORM: Full-Screen Feed (catalog challenger pop-culture-shelf-vertical-video-feed-surface, the owner's pick over the dealt Postmarked), turned sideways to match the owner's gestures. seed:9f96972bde8fa19e
DEVIATIONS (disclosed after the #118 build): Chip in is a white button on each ask, not a rail glyph, so the money action travels with the person. The rail holds Back, Next, and the count, and Show less joins it in #119. Share is left out of #118's scope and filed as PB-44. The nav shows the signed-in username in place of "You", so people can see whose account they're in.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
