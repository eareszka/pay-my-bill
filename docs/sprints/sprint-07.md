# Sprint 7: Safe to open

**Dates:** 2026-11-18 → 2026-11-24 · **Goal:** a blocked person disappears, reminders run on their own, failures get noticed, and the App Store pack is ready (roadmap Phase 3, plus Phase 4 ops)

Draft: the owner confirms the order and the "Needs the owner" picks at planning.

## Committed
| Story | Issue | Lane | Points | Status |
|---|---|---|---|---|
| PB-12 Block another user | #257 | main | 3 | In progress |
| PB-35 Scheduled jobs for reminders | #258 | main | 1 | To do |
| Send email off the request path, prune login_attempts | #15 | main | 2 | To do |
| PB-15 Monitoring and backups | #259 | main | 2 | Needs the owner's tracker pick |
| PB-23 Reaction counts in the admin queue | #73 | main | 1 | To do |
| Keep a payment handle while a post is open | #21 | main | 2 | To do |
| PB-51 Retry photo deletes that fail | #149 | main | 1 | To do |
| Support page for the App Store listing | #264 | main | 1 | To do |
| PB-19 App Store listing and review pack | #260 | ui | 3 | Pack in review (#263); blocked on #264, #265, #257, PB-39, demo account |
| Bubble tails flicker (from Sprint 6) | #225 | ui | — | Waiting on the owner's phone recheck |
| *Stretch 1:* Optional tip, web only, replacing the 1% fee | #265 | main → ui | 5 | To do |
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
