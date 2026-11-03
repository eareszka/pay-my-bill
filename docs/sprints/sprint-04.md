# Sprint 4: Follow-through

**Dates:** 2026-11-02 → 2026-11-08 · **Goal:** posts can close, posters report back or can't post again, and people can respond to what they read

The owner chose the scope and the rules. See the amendments in ADR 0008.

## Committed
| Story | Issue | Points | Status |
|---|---|---|---|
| S4-1 Close a post, and auto-close after 30 days | #65 | 3 | Done |
| S4-2 Post a results update | #26 | 5 | Done |
| S4-3 Block new posts while an update is overdue, with reminders | #27 | 3 | Done |
| S4-4 Kudos and reactions on results updates | #64 | 3 | Done |
| S4-5 Follow-through stat on profiles | #28 | 2 | Done |

**Total:** 16 points (Sprint 3: 13).

## Daily log
- 2026-11-02: Planned with the owner. Did #65: closing a post and the 30-day auto-close. The review changed "I sent it" on a closed post from a bare 404 to a clear message, made the date shown the last full day a post is open, and gave seed posts a close date. PB-20 to PB-22 went to the backlog: update photos, recording a gift sent just before closing, and starting the clock when a flagged post is approved. Next: #26 results updates. Blocked: none.
- 2026-11-02: #65 merged (#66). Did #26: results updates. Next: #27 overdue block and reminders. Blocked: none.
- 2026-11-02: The #26 review added a notice for donors confirmed after the update, a fundraising check on notes, clearer delete prompts, and cleaner text handling. Sending these emails during the request stays with #15. Blocked: none.
- 2026-11-02: #26 merged (#70). Did #27: the overdue block and reminders. Next: #64 kudos and reactions. Blocked: none.
- 2026-11-02: The #27 review stopped a late confirmation from lifting the block, restarted reminders when the deadline moves, and moved reminders to calendar days so they land before the date they name. Blocked: none.
- 2026-11-02: #27 merged (#71). Did #64: kudos and reactions. Next: #28 follow-through stat. Blocked: none.
- 2026-11-02: The #64 review made a double tap safe, removed a deleted account's reactions, and hid buttons that couldn't work. PB-23 went to the backlog for showing 🤨 counts in the admin queue. Blocked: none.
- 2026-11-02: #64 merged (#72). Did #28: the follow-through stat. Next: the finish review, then Sprint 4 Review. Blocked: none.
- 2026-11-02: The #28 review added test cases for auto-closed and deleted posts and late confirmations. Impeccable's finish review of the post page and profile, at 360px and 1440px in both themes, made the due date stand out, explained what 👍 and 🤨 mean and who can use them, showed the 20-character minimum up front, and explained the stat on profiles. The full loop passed on a migrated, seeded database. Next: Sprint 4 Review. Blocked: none.
- 2026-11-03: After Sprint 4, the owner answered #67 (allow 24 hours) and asked for a complete redesign with Impeccable, choosing Seed Packet with a rack-style feed instead of a scrolling column. Filed #75 and did it on PR #76, with the code and finish reviews. Photos on posts are next to plan. Blocked: none.
