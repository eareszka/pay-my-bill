# Product Backlog

Stories and spikes that aren't in a sprint yet. Pull them in at Sprint Planning. UI stories still need a wireframe to meet the Definition of Ready. Stories that depend on donations (PB-1 to PB-4) can't start until Sprint 2's confirm flow is merged.

---

### PB-1 Post a results update · #26 · 5 pts · P1 · epic:posts
As a **recipient**, I want to **tell donors how their help was used** so that **they see it mattered**. (ADR 0008)
- [ ] Given my post closed with at least one confirmed donation, when I open it, then I see a prompt to post an update.
- [ ] Given a note under 20 characters, when I submit, then it's rejected with a message.
- [ ] Given an optional photo, when I upload it, then the type and size are validated and it's stored under a random filename (T7).
- [ ] Given I post the update, then it shows on the post and every donor with a confirmed donation is emailed.
- [ ] The form says receipts are never required and warns against sharing account numbers or medical details (T14).
- [ ] Kudos and 👍/🤨 reactions can be added to an update; 🤨 counts are visible to admins.

### PB-2 Block posting while an update is overdue · #27 · 3 pts · P1 · epic:safety
As the **community**, we want **recipients to follow through** so that **people can't collect and vanish** (T12).
- [ ] Given a post that owes an update, when 3 and 6 days have passed since it closed, then the recipient gets a reminder email.
- [ ] Given an update is more than 7 days overdue, when the recipient tries to create a post, then they're sent to the overdue post with an explanation.
- [ ] Given they post the overdue update, when they try again, then posting works right away.
- [ ] Overdue status is computed from dates, not a cron-only flag, so a missed job can't block or unblock anyone wrongly.

### PB-3 Follow-through stat on profiles · #28 · 2 pts · P2 · epic:rewards
- [ ] Given a user with posts that owed updates, when anyone views their profile, then it shows "Updated N of M funded posts."
- [ ] Given a user with no posts that owed updates, then the stat isn't shown.

### PB-4 Auto-expire pending donations · #29 · 2 pts · P1 · epic:donations
- [ ] Given a donation `pending` for 3 days, then the recipient gets one reminder to confirm or dispute.
- [ ] Given a donation `pending` for 14 days, then it becomes `expired` and earns nothing (ADR 0004, T15).
- [ ] The donor sees the expired status on their history.

### PB-5 18+ attestation at signup · #30 · 1 pt · P0 · epic:accounts
- [ ] Given the signup form, when I don't confirm I'm 18 or older, then no account is created.
- [ ] The attestation time is stored on the user (T13).

### PB-6 Delete my post and my account · #31 · 3 pts · P1 · epic:accounts
- [ ] Given my open post with no confirmed donations, when I delete it, then it's gone from the feed and returns 404.
- [ ] Given a post with confirmed donations, when I delete it, then the text and photo are removed but donors keep their credit.
- [ ] Given I delete my account after confirming my password, then my profile, handles, and posts are removed or anonymized and I'm logged out (T14).

### PB-7 Terms of Service and Privacy Policy pages · #32 · 2 pts · P0 · epic:safety
- [ ] `/terms` and `/privacy` exist and are linked in the footer and on the signup form.
- [ ] Terms state: 18+, no business fundraising, the app never holds money, needs aren't verified, and donations are gifts at the donor's own risk.
- [ ] Marked as drafts; a lawyer review is a v1.0 gate (PRD).

### PB-8 Staging Postgres before it expires · #33 · 1 pt · P0 · chore
- [ ] Before 2026-11-26, staging Postgres is either on a paid plan or recreated, with the steps written in the README.

### PB-9 Spike: payment-app terms · #34 · 2 pts · P1 · spike
- [ ] A short write-up in `docs/research/` on what Cash App, Venmo, and PayPal allow for soliciting personal payments, deep-link rules, and 1099-K implications for recipients.
- [ ] Any required changes become backlog items or a new ADR.

### PB-10 Spike: product name and domain · #35 · 2 pts · P2 · spike
- [ ] Three or more candidate names, each checked against USPTO search, domain availability, and app-store conflicts.
- [ ] The owner picks one; an ADR records it.

### PB-11 Spike: cold start and beta recruitment · #36 · 2 pts · P2 · spike
- [ ] A plan for getting the first 20–50 beta users, including where donors come from, and how the PRD success metrics will be measured.
