# Sprint 7: Safe to open

**Dates:** 2026-11-18 → 2026-11-24 · **Goal:** a blocked person disappears, reminders run on their own, failures get noticed, and the App Store pack is ready (roadmap Phase 3, plus Phase 4 ops)

Draft: the owner confirms the order and the "Needs the owner" picks at planning.

## Committed
| Story | Issue | Lane | Points | Status |
|---|---|---|---|---|
| PB-12 Block another user | #257 | main | 3 | Done |
| PB-35 Scheduled jobs for reminders | #258 | main | 1 | Done |
| Send email off the request path, prune login_attempts | #15 | main | 2 | Done |
| PB-15 Monitoring and backups | #259 | main | 2 | Done |
| PB-23 Reaction counts in the admin queue | #73 | main | 1 | Done |
| Keep a payment handle while a post is open | #21 | main | 2 | Done |
| PB-51 Retry photo deletes that fail | #149 | main | 1 | Done |
| Support page for the App Store listing | #264 | main | 1 | Done |
| PB-19 App Store listing and review pack | #260 | ui | 3 | Done |
| Create a post one question per screen (owner's ask) | #275 | main → ui | — | Done |
| Post tab lists your posts (owner's ask) | #278 | main → ui | — | Done |
| Up to 5 photos per post, first required (owner's ask) | #279 | main → ui | — | Done |
| Bubble tails flicker (from Sprint 6) | #225 | ui | — | Waiting on the owner's phone recheck |
| *Stretch 1:* Optional tip, web only, replacing the 1% fee | #265 | main → ui | 5 | Done |
| *Stretch 2:* PB-52 Push notifications in the iOS app | #261 | main → ui | 8 | To do |

**Total:** 16 points, plus 13 stretch (Sprint 6: 13 of 13).

## Needs the owner
- **Costs and accounts:** PB-13 paid hosting (prices first), PB-48 photos on our own domain, PB-18 Apple enrollment (TestFlight already runs, so likely done), PB-35 only if the scheduler costs money.
- **Legal and research:** PB-39 lawyer review, #34 payment-app terms, #36 beta recruitment.
- **Design and rules:** #98 chip-in redesign, #89 board decisions (may be stale after the redesign), #87 and #88 stack behavior, #124–#127 messaging guardrails, #146 farm detection.

## Daily log
- 2026-11-18: Drafted from the roadmap and main's order. Opened #257–#261 and labeled the lanes. Next: the owner confirms. Blocked: none.
- 2026-11-18 (ui): #260: App Store pack drafted (listing, privacy label, review notes, screenshots). Blockers: card-gift 1% fee vs 3.2.1(vii), /support page, #257, demo account.
- 2026-11-18: Owner chose an optional tip on the web only in place of the 1% fee (#265). Added #264 support page. Blocked: none.
- 2026-11-18 (ui): #257 design on #266: Block asks first in place (owner's pick), sits quietly under Report, and Settings → Blocked is a hairline list. Blocked: none.
- 2026-11-18 (ui): #265 design on #273: the web tip is one row of pills (No tip, $1, $2, Other), and Other's amount box shows only when picked. Blocked: none.
- 2026-11-18 (main): #275: new post asks one question per screen (owner's Hinge/Bumble ask), with progress bar, auto-next on picks, and errors opening on their step. Next: ui. Blocked: none.
- 2026-11-18 (ui): #275 look: League Gothic questions (owner's pick), need/want rows that tick, emoji pills, a round → in thumb reach, slide between steps. Blocked: none.
- 2026-11-18 (main): #278: the Post tab lists your posts under Create new post, and stays highlighted on the questions. Next: #279, five photos. Blocked: none.
- 2026-11-18 (ui): #278 look on #280: Create new post is a full-width pill with the post icon, and the empty list drops its duplicate link. Next: #281 photos. Blocked: none.
- 2026-11-18 (main): #279: five photo boxes on new posts, first required (ADR 0020); cover stays the feed photo, all photos deleted together. Next: ui. Blocked: none.
- 2026-11-18 (ui): #279 look on #281: photo boxes are a 4:5 grid with a green + and a Cover tag, error and focus states, and the post's extra photos as tiles. Blocked: none.
- 2026-11-19 (main): Merged #280 (#278) and #281 (#279). Table: merged stories marked Done, duplicate #279 row removed. Left: #261 (Apple enrollment), #225, #282. Blocked: none.
- 2026-11-19 (main): #282: post sheet shows the whole person (bio, poster card, stats, photos interleaved) and a Chip in button for visitors. Next: ui. Blocked: none.
