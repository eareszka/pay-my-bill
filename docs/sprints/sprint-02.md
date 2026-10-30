# Sprint 2: People can chip in

**Dates:** 2026-11-09 → 2026-11-15 · **Goal:** a donor can pay a poster through Cash App, Venmo, or PayPal, record it, and see it count once the poster confirms

Pulled forward on 2026-10-30, because Sprint 1 finished early. The owner picked the stories and the layouts.

## Committed
| Story | Issue | Points | Status |
|---|---|---|---|
| S2-1 Donation model + migration | #46 | 2 | Done |
| S2-2 Pay-app buttons with the amount prefilled | #43 | 2 | In review |
| S2-3 Record a gift with "I sent it" | #45 | 3 | To do |
| S2-4 Confirm or dispute gifts on /gifts | #44 | 3 | To do |
| Auto-expire pending gifts after 14 days | #29 | 2 | To do |
| 18+ attestation at signup | #30 | 1 | To do |
| Delete my post and my account | #31 | 3 | To do |

**Total:** 16 points (Sprint 1 velocity: 23).

**Owner action:** recreate the staging database before 2026-11-26 (#33; steps are in the README).

## Daily log
- 2026-10-30: Merged the roadmap (#41) and the staging DB steps (#42). Planned Sprint 2 and filed #43–#46. Claimed #46. Next: the Donation model. Blocked: none.
- 2026-10-30: #46 merged (#47). The review added delete-with-post for gifts, a single selectin load, and seed timestamps in order. Skipped for now: a SQL aggregate and extra CHECKs. Did #43: pay-app buttons with the amount prefilled by a small script. Next: #45 "I sent it". Blocked: none.
