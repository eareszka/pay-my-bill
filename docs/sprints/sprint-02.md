# Sprint 2: People can chip in

**Dates:** 2026-11-09 → 2026-11-15 · **Goal:** a donor can pay a poster through Cash App, Venmo, or PayPal, record it, and see it count once the poster confirms

Pulled forward on 2026-10-30, because Sprint 1 finished early. The owner picked the stories and the layouts.

## Committed
| Story | Issue | Points | Status |
|---|---|---|---|
| S2-1 Donation model + migration | #46 | 2 | Done |
| S2-2 Pay-app buttons with the amount prefilled | #43 | 2 | Done |
| S2-3 Record a gift with "I sent it" | #45 | 3 | Done |
| S2-4 Confirm or dispute gifts on /gifts | #44 | 3 | Done |
| Auto-expire pending gifts after 14 days | #29 | 2 | Done |
| 18+ attestation at signup | #30 | 1 | Done |
| Delete my post and my account | #31 | 3 | Done |

**Total:** 16 points (Sprint 1 velocity: 23).

**Owner action:** recreate the staging database before 2026-11-26 (#33; steps are in the README).

## Daily log
- 2026-10-30: Merged the roadmap (#41) and the staging DB steps (#42). Planned Sprint 2 and filed #43–#46. Claimed #46. Next: the Donation model. Blocked: none.
- 2026-10-30: #46 merged (#47). The review added delete-with-post for gifts, a single selectin load, and seed timestamps in order. Skipped for now: a SQL aggregate and extra CHECKs. Did #43: pay-app buttons with the amount prefilled by a small script. Next: #45 "I sent it". Blocked: none.
- 2026-10-30: #43 merged (#48). The review fixed a comma being read as a decimal point (a 100x prefill), switched to Venmo's documented `recipients=` link, added an inline amount error and a sync on page load, and hid the buttons from the poster. Did #45: "I sent it" records a pending gift and emails the poster. Checked at 360px: the donor view and the error view, with one error message shown at a time. Next: #44 `/gifts` confirm or dispute. Blocked: none.
- 2026-10-30: #45 merged (#49). The review fixed Enter submitting the form, an unpicked app defaulting to the first one, repeat claims (now one pending gift per donor per post), gifts larger than the goal, a race with closing posts (row lock), and CSRF tokens expiring while donors were in their payment app. The owner made Impeccable required for frontend design. It's installed globally, with its design hook and PRODUCT.md written through `/impeccable init`. Did #44: `/gifts` with confirm, an inline dispute confirmation, sent-gift statuses, and the top-bar count, designed with Impeccable and checked at 360, 390, and 1440 in both themes. Next: the Impeccable finish review and code review for #44, then #29, #30, and #31. The design polish pass on existing pages follows as its own PR. Blocked: none.
- 2026-10-31: #44 merged (#50). The code review added a post-row lock before funding, dropped removed posts, and dropped the UTC date. Impeccable's finish reviewer moved the dispute spacing, button heights, the badge's screen-reader text, the empty-state copy, and the ledger columns, then shipped. Did #29: expiry worked out from the gift's date, an Expired status, and `flask gifts remind` with `reminded_at` (migration 0004). Next: #30, then #31. Blocked: none.
- 2026-10-31: #29 merged (#51). The review made reminders commit per poster (no repeats after a failure), took links straight from `APP_URL`, and let expired gifts still be disputed. Did #30: the 18+ checkbox at signup, stored in `adult_attested_at`. Next: #31. Blocked: none.
- 2026-10-31: #30 merged (#52). Did #31: delete a post or the account, with inline confirms (the owner chose anonymizing and inline steps). Next: the review for #31, then the beta-ready polish pass. Blocked: none.
- 2026-10-31: #31 merged (#53). The review added a post lock, kept gifted posts as scrubbed shells, ended deleted accounts' sessions, rate-limited the password, and cleared login history. All 16 points are done. Did #54: the beta-ready Impeccable polish pass across every page. Two inspection rounds at 360 in both themes, and the detector is clean on the rendered pages. Next: Sprint Review and Retro (owner), then Sprint 3 planning. Blocked: none.
