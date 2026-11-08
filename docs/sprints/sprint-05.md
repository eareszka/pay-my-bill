# Sprint 5: Ready for real people

**Dates:** 2026-11-03 → 2026-11-09 · **Goal:** real gifts can't get lost, donors can see who they're helping and what their giving earned, and failures have a way forward

The owner chose this sprint after Impeccable's audit and critique, ahead of photos and the safety work.

## Committed
| Story | Issue | Points | Status |
|---|---|---|---|
| S5-1 Harden errors, accessibility, and small screens | #77 | 5 | Done |
| S5-2 Safer chip-in flow | #78 | 5 | Done |
| S5-3 Trust information | #79 | 3 | To do |
| S5-4 Visible rewards | #80 | 5 | To do |
| S5-5 Clear disputes | #81 | 3 | To do |
| S5-7 Bulletin board and the top spot | #85 | 5 | Done |
| S5-6 Password reset | #82 | 3 | To do |

**Total:** 29 points (Sprint 4: 16).

## Daily log
- 2026-11-03: Planned with the owner, who approved the order and chose an email plus a Gifts banner for confirmed gifts, and dates plus an optional payment-app name for matching. Did #77: hardening. Next: #78 safer chip-in. Blocked: none.
- 2026-11-03: The #77 review kept the 500 page working when the database is down, fixed comma amounts that could inflate a pay link, stopped redirects from scrolling past confirmation messages, and made stale forms return only to pages that can open. Static caching waits for production hosting. Blocked: none.
- 2026-11-03: #77 merged (#83). Did #78: the safer chip-in flow. Next: #79 trust information. Blocked: none.
- 2026-11-03: The #78 review hid the Not yet button until it's needed, kept the remembered gift until the server has it, and made the late window honest. The remembered amount lasts only in its tab, so verifying email in a new tab loses it. Blocked: none.
- 2026-11-03: #78 merged (#84). The owner found the rack too cluttered and chose a bulletin board with a large top ticket and no thumbtacks, then decided the top spot should reward follow-through (ADR 0013). Did #85. Next: review it with the owner, then #79. Blocked: none.
- 2026-11-03: The owner found the grid of small tickets still cluttered and too much like a scroll site, and chose One Ticket at a Time on #85. Waiting on the owner's review of the look. Blocked: none.
- 2026-11-03: The owner approved One Ticket at a Time on phones and chose Give Right Here for the website. The #85 review closed more ways to game the first ticket. PB-24 and PB-25 went to the backlog. Blocked: none.
- 2026-11-03: The owner tried the full-browser layout and asked to go back to the earlier size, so it was reverted. Waiting on the owner's review of the look. Blocked: none.
- 2026-11-03: The owner approved the layout. The #86 code review found an update and a late gift form overlapping on wide screens, feed logins losing the post, and kudos cancelling 🤨 past the cap; all fixed. Loading the first ticket on every feed view costs more as history grows; left for now, to revisit with real traffic. Blocked: none.
- 2026-11-03: The finish review's contrast, line length, and dark stack fixes went in. Its suggestions to replace the reaction emoji, recolor links and marks, and put Rules and profile text on tickets would change the approved look, so they wait for the owner. Blocked: none.
- 2026-11-04: #85 is complete and approved by the owner, with PR #86 open and not merged. Complete: the bulletin board with One Ticket at a Time on phones and Give Right Here on computers, the top spot that rewards follow-through, the code review and finish review fixes, and a rewritten `DESIGN.md`. 550 tests pass at 100% coverage. Waiting on five owner decisions: reaction emoji, green links and marks, Rules and profile text on cork, where "I sent it" lands, and a Need or Want label on phones. Loading the first ticket on every feed view still costs more as history grows; revisit with real traffic. Next: #79 trust information. Blocked: none.
- 2026-11-04: The owner chose to merge #85 (#86) now and build swiping on its own PR. The five open decisions move to a follow-up issue. Blocked: none.
- 2026-11-04: The owner restated the concept and chose whole-stack ranking with new posts spaced in, rewards at the right moment plus perks that unlock, a one-tap thank you, removing local area, and web first, then the App Store. Added PB-27 to PB-40 and rewrote the roadmap; none of it joins this sprint. Blocked: none.
- 2026-11-08: The owner chose to launch tonight. #79, #80, and #81 are paused for Sprint 5b (`sprint-05b.md`), and they resume after launch. Blocked: none.
