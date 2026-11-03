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
| S5-7 Bulletin board and the top spot | #85 | 5 | In review |
| S5-6 Password reset | #82 | 3 | To do |

**Total:** 29 points (Sprint 4: 16).

## Daily log
- 2026-11-03: Planned with the owner, who approved the order and chose an email plus a Gifts banner for confirmed gifts, and dates plus an optional payment-app name for matching. Did #77: hardening. Next: #78 safer chip-in. Blocked: none.
- 2026-11-03: The #77 review kept the 500 page working when the database is down, fixed comma amounts that could inflate a pay link, stopped redirects from scrolling past confirmation messages, and made stale forms return only to pages that can open. Static caching waits for production hosting. Blocked: none.
- 2026-11-03: #77 merged (#83). Did #78: the safer chip-in flow. Next: #79 trust information. Blocked: none.
- 2026-11-03: The #78 review hid the Not yet button until it's needed, kept the remembered gift until the server has it, and made the late window honest. The remembered amount lasts only in its tab, so verifying email in a new tab loses it. Blocked: none.
- 2026-11-03: #78 merged (#84). The owner found the rack too cluttered and chose a bulletin board with a large top ticket and no thumbtacks, then decided the top spot should reward follow-through (ADR 0013). Did #85. Next: review it with the owner, then #79. Blocked: none.
