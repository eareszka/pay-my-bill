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
| S5-8 Swipe through the pile | #90 | 3 | Done |
| S5-9 New look: the card stack | #118 | 8 | In progress |
| S5-10 Categories and show less | #119 | 5 | To do |
| S5-11 How-it-works home page | #120 | 5 | To do |
| S5-12 Photo on a post | #122 | 5 | In progress |

**Total:** 55 points (Sprint 4: 16).

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
- 2026-11-04: #85 merged (#86). The owner described the feed as swiping through mail and bills and added #90: swipe left for next and right for back, with motion only and no new look. The five open decisions moved to #89. Waiting on the owner's review of the feel. Blocked: none.
- 2026-11-04: The owner found that swiping showed a blank page before the next post loaded. The neighboring posts now sit in the page, so a swipe reveals one straight away, and the Chip in panel can't be used until the new page loads. Waiting on the owner's review of the feel. Blocked: none.
- 2026-11-04: The owner restated the concept and chose whole-stack ranking with new posts spaced in, rewards at the right moment plus perks that unlock, a one-tap thank you, removing local area, and web first, then the App Store. Added PB-27 to PB-40 and rewrote the roadmap; none of it joins this sprint. Blocked: none.
- 2026-11-08: The owner chose to launch tonight. #79, #80, and #81 are paused for Sprint 5b (`sprint-05b.md`), and they resume after launch. Blocked: none.
- 2026-11-09: #90 merged (#91) after merging main into it; CI green, 647 tests at 100%. The owner asked for a new look that doesn't read as AI-made, modeled on dating-app swiping: replace the cork board through Impeccable, add post categories with a "show less" that pushes a category down the stack (swipe down or a button), and a scroll-driven how-it-works home page for new visitors. Added S5-9 (#118), S5-10 (#119), and S5-11 (#120). Started #118 with the Impeccable direction round. Next: the owner picks a direction. Blocked: none.
- 2026-11-09: On the Impeccable decision page, the owner chose Full-Screen Feed over the dealt Postmarked, kept their own gestures (left next, right back, down show less), and chose category colors, a tall stage beside Chip in on desktop, and a dark feed with system-themed forms. Built #118: new shell, bottom nav, full-screen ask cards, rail, post page header, and every page restyled. 647 tests pass at 100%. Next: the finish review, then the new `DESIGN.md`. Blocked: none.
- 2026-11-09: The #118 finish review asked for 8 fixes, all applied and scored resolved (ship); PR #121 is open. The owner asked for placeholder photos to test uploads, then chose the full upload story (#122): R2 storage, shown right away but reportable, one photo per post. Built it on top of #118 with ADR 0015, migration 0014 (after 0012; re-point it if #116's 0013 lands first), and CC0 seed photos from Wikimedia Commons. 681 tests pass at 100%. Blocked: the owner needs a Cloudflare R2 bucket and five `R2_*` settings on Render before staging keeps photos.
