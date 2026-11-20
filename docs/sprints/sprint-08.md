# Sprint 8: Share and photos

**Dates:** 2026-11-19 → 2026-11-25 · **Goal:** people can share an ask, a results update can show a photo, and photos load from our own domain ([backlog](../backlog/product-backlog.md))

## Committed
| Story | Issue | Lane | Points | Status |
|---|---|---|---|---|
| PB-48 Photos on our own domain | #289 | main + owner | 1 | Steps in README; waiting on the owner |
| PB-44 Share an ask | #288 | main → ui | 2 | Removed for now by the owner (#298) |
| PB-20 Photo on a results update | #69 | main → ui | 2 | Done (#293) |
| PB-52 Push notifications in the iOS app (from Sprint 7) | #261 | main → ui | 8 | Blocked: APNs key from the owner's Apple account |
| Bubble tails flicker (from Sprint 6) | #225 | ui | — | Waiting on the owner's phone recheck |
| Post sheet: full-screen photo, emoji pills, round Chip in (owner's ask) | #295 | ui | — | In review |

**Total:** 5 points, plus 8 carried (Sprint 7: 21 of 16).

## Needs the owner
- **#289:** connect the photo domain in Cloudflare (main writes the steps).
- **#261:** the push key from the Apple Developer account. **#225:** recheck on the phone.
- **Next sprint's picks:** PB-13 hosting, PB-39 lawyer, #34, #36, #98, #124–#127, #146.

## Daily log
- 2026-11-19: Owner picked PB-44, PB-20, and PB-48. Opened #288 and #289, carried #261 and #225. Blocked: none.
- 2026-11-19 (main): #289: Cloudflare steps for photos.yearnly.app in the README; no code change (CSP follows R2_PUBLIC_URL). Next: #288 Share. Blocked: owner does the steps.
- 2026-11-19 (main): #288: Share on the rail and post page (share sheet, else copy link; bare post URL). Next: ui, then #69. Blocked: none.
- 2026-11-19 (ui): #288 look on #292: Share is the last rail glyph (Back gutter on desktop) and a pill left of × on the post; falls back to copying in the iOS shell. Blocked: none.
- 2026-11-19 (main): #69: optional photo on a results update (same checks as post photos, never a receipt). Next: ui; #261 waits on the APNs key. Blocked: none.
- 2026-11-19 (ui): #69 look on #293: update photo is one box from the new-post grid; a posted one fills the panel width (no sideways scroll). Blocked: none.
- 2026-11-19: #69 merged (#293). 4 of 5 points done; #289 waits on the owner's Cloudflare steps, #261 on the APNs key, #225 on the recheck. Blocked: owner.
- 2026-11-19: #295: post sheet photo fills the first screen, facts and poster stats are emoji pills, Chip in is a round gift button that stays put. Blocked: none.
- 2026-11-19: #295 owner follow-up: Chip in is its own page; a chat disc beside it opens a labeled mock chat. Both discs stay put. Blocked: none.
- 2026-11-20 (main): #298: reverted #292, so Share is gone from the rail and post page (owner: not for now). Next: merge #296/#297. Blocked: none.
