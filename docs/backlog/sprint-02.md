# Sprint 2 Backlog: "People can chip in"

The owner chose the stories, the gift flow, and the screen layouts on 2026-10-30. Gifts are link-out only (ADR 0002), and only recipient-confirmed gifts count (ADR 0004).

---

### S2-1 Donation model + migration · #46 · 2 pts · P0 · type:chore
- [ ] A `Donation` model with post, donor, amount in cents, method (Cash App, Venmo, PayPal), status (`pending`, `confirmed`, `disputed`), created and resolved times. Migration 0003.
- [ ] The amount must be over $0 and at most $1,000 (a DB CHECK).
- [ ] `Post.raised_cents` sums only confirmed gifts, so feed and post progress bars are real.
- [ ] `flask seed` adds a few gifts in each status.

### S2-2 Pay-app buttons with the amount prefilled · #43 · 2 pts · P0 · epic:donations
As a **donor**, I want to **type an amount once and tap my app** so that **it opens ready to pay**.
- [ ] Given an open post, when I enter an amount, then the Cash App, Venmo, and PayPal buttons for the poster's handles open with that amount prefilled.
- [ ] Given JavaScript is off, then the buttons still open the poster's page in each app, without the amount.
- [ ] Only the apps the poster has handles for are shown.

### S2-3 Record a gift with "I sent it" · #45 · 3 pts · P0 · epic:donations
As a **donor**, I want to **say what I sent** so that **the poster can confirm it and I get credit**.
- [ ] Given I'm verified and not the poster, when I submit "I sent $X via <app>" on an open post, then a `pending` gift is recorded and the poster is emailed.
- [ ] Given I'm logged out or unverified, then I'm sent to log in or verify first.
- [ ] Given the poster, a closed post, or an amount outside $0.01–$1,000, then nothing is recorded.
- [ ] Pending gifts don't move the progress bar.

### S2-4 Confirm or dispute gifts on /gifts · #44 · 3 pts · P0 · epic:donations
As a **poster**, I want to **confirm the gifts I actually received** so that **progress and donor credit are honest** (T1).
- [ ] `/gifts` has "To confirm" (pending gifts to my posts) and "My gifts" (gifts I sent, with status).
- [ ] Given a pending gift to me, when I tap Confirm or Dispute, then its status and resolved time are set. Only the recipient can do this.
- [ ] Given confirmed gifts reach the goal, then the post becomes `funded` and leaves the feed.
- [ ] The top bar shows a count badge when gifts are waiting for me.

### #29 Auto-expire pending gifts after 14 days · 2 pts · P1 · epic:donations
- [ ] A gift pending for more than 14 days shows as `expired`, can't be confirmed, and earns nothing (T15). This is computed from its date; there's no cron.
- [ ] `flask gifts remind` emails recipients once about gifts pending for 3 or more days. It gets scheduled when production exists (roadmap Phase 2).

### #30 18+ attestation at signup · 1 pt · P0 · epic:accounts
- [ ] As in the product backlog (PB-5).

### #31 Delete my post and my account · 3 pts · P1 · epic:accounts
- [ ] As in the product backlog (PB-6). Deleting an account anonymizes the user so donors keep credit.

---

## Wireframes (phone width, 360px)

```
S2-2/S2-3 post page (open)        S2-4 /gifts
+----------------------------+    +----------------------------+
| Pay My Bill   Gifts(2) ... |    | Pay My Bill   Gifts(2) ... |
| NEED · maria_g · Tampa, FL |    | To confirm                 |
| Short on rent this month   |    | $20 via Venmo from dev_tom |
| [=====-------] $120 / $300 |    | on "Short on rent"         |
| story text...              |    | [ Confirm ] [ Dispute ]    |
|                            |    | -------------------------- |
| Chip in                    |    | My gifts                   |
| [ $ 20.00               ]  |    | $15 to kayla.r  Confirmed  |
| [Cash App][Venmo][PayPal]  |    | $10 to lee_w    Pending    |
|                            |    | $5 to sam_helps Expired    |
| Sent it?                   |    +----------------------------+
| [ I sent $20 via [app v] ] |
| Pay My Bill never holds    |
| money.                     |
+----------------------------+
```
