# Design session, 2026-11-09

This is a record of what the owner asked for and decided in one working session, so later work can build on it without re-asking. The decisions themselves also live in DESIGN.md, ADR 0015, the surface brief (`.impeccable/surfaces/app-templates-base-html.md`), and the backlog. This page ties them together.

## What the owner asked for
> Get the design down and not look AI-generated. Use Impeccable to restyle, and put coherence and simplicity first. Mobile and desktop should both work and share one style. The inspiration is dating apps like Tinder or Bumble, where you swipe through people's wants and needs, except you can go back, and you can choose to see less of a kind of want. Animations should be fast, readable, and stylized. The sign-up page should use scroll-driven animation.

## Decisions and where they shipped

| Topic | Decision | Shipped in |
|---|---|---|
| Process | Merge the swipe PR first, then one story per PR in Sprint 5 | #91 merged |
| Visual world | Replace the cork board through Impeccable's direction round. The owner picked **Full-Screen Feed** (each ask fills the screen) over the dealt Postmarked, Guest Check, Ticket Wallet, and the Tinder-style standard | #118 → PR #121 |
| Gestures | Left = next, right = back, down = show less (coming in #119), with buttons for each. No vertical-snap feed | #118 |
| Field color | Each ask is a saturated category color: Need red and Want blue until categories land | #118 |
| Themes | The feed and post pages are always dark. Forms, Gifts, Leaders, and the profile follow the system light or dark setting | #118 |
| Desktop | First a tall stage beside Chip in. The owner found that phone-shaped card counterintuitive on a monitor and chose **wide card + side arrows**: the feed card takes the post page's shape, with big Back and Next outside it and arrow keys, so no dragging is needed | #118 → PR #121 |
| Motion | 180ms throw, 200ms settle, a 4° tilt, and the rail glyph lights toward the drag target. Reduced motion gets a fade | #118 |
| Photos | Full upload story: Cloudflare R2, shown right away but reportable, one photo per post. Location data is stripped. The dev seed uses CC0 photos | #122 → PR #123, ADR 0015 |
| Flicker | Neighbor photos load and decode on page open, the visible photo is drawn first, and the old page stays until the next one is ready | PR #123 |
| Show less | Post categories. Show less pushes a category down the stack and never hides it, with undo. The category list is not confirmed yet | #119 (to do) |
| Home page | A scroll-driven how-it-works page for logged-out visitors that ends at sign-up | #120 (to do) |
| Messages | Four stories, no threads: a note with your gift (#124), a thank-you with a reply (#125), progress updates with following (#126), and questions before giving (#127) | Backlog, PR #128 |
| Messages design | One **"How it's going"** list per post (updates, shared gift notes, answered questions, newest first, the same item shape, at most one reply). Chip in comes first, Follow is one quiet button, notes sit behind a link, the thank-you opens inside the gift, and the feed card gets one "Updated" line | Approved mockup: `docs/design/mockups/post-messages.html` (also https://claude.ai/artifact/5MUbEMb4eFFSVL7k9tS86n) |

## Still open
- **Owner:** set up Cloudflare R2 and the five `R2_*` settings on Render. Until then, photos on staging are lost on each redeploy. The steps are in PR #123.
- **Owner:** confirm the #119 category list. The draft is Rent and housing, Bills and utilities, Groceries and food, Car and transport, Health, Kids and school, Fun and games, and Other.
- **Owner:** keep the Venmo and PayPal buttons filled next to "Chip in instantly", or make them outlined?
- **Owner:** should "donor" go from the copy, like "donation"?
- Share button: PB-44.
- Migration 0014 follows 0012. If #116's migration 0013 (PR #117) merges, re-point it.
- Next in order: #119, then #120, then the message stories.
