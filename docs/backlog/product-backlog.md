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

---

## Toward the App Store (see `docs/roadmap.md`)

### PB-12 Block another user · #TBD · 3 pts · P1 · epic:safety · v0.1-alpha
As a **user**, I want to **block someone** so that **I stop seeing them and they can't interact with me** (App Store Guideline 1.2).
- [ ] Given another user's profile or post, when I block them, then their posts and updates are hidden from my feed.
- [ ] Given they've blocked me or I've blocked them, then neither of us can pledge to the other's posts or give kudos.
- [ ] Given my blocked list in settings, when I unblock someone, then their content shows again.
- [ ] Blocking is silent: the blocked user isn't notified.

### PB-13 Production hosting, domain, and HTTPS · #TBD · 3 pts · P0 · chore · v0.2-beta
- [ ] ADR 0010 records the production host, plan, and monthly cost.
- [ ] Production auto-deploys from tagged releases, separate from staging, on the domain chosen in PB-10, with HTTPS.
- [ ] `SESSION_COOKIE_SECURE` and the other production settings come from env vars and are listed in `.env.example`.

### PB-14 Transactional email provider · #TBD · 2 pts · P0 · epic:accounts · v0.2-beta
- [ ] `MAIL_SERVER` points at a provider (Postmark, Resend, or SES) with SPF and DKIM set up on the domain.
- [ ] A verification email from production lands in the Gmail and iCloud inboxes, not spam.

### PB-15 Monitoring and backups · #TBD · 2 pts · P1 · chore · v0.2-beta
- [ ] Unhandled errors are reported to an error tracker, with no passwords or tokens in the payload.
- [ ] An uptime check on `/health` alerts the owner.
- [ ] Daily Postgres backups, and a restore that's been tested once and written down in the README.

### PB-16 Spike: Capacitor iOS wrapper · #TBD · 3 pts · P1 · spike · v1.0
- [ ] A Capacitor project that loads the production site, with a write-up in `docs/research/`.
- [ ] A plan for the native features that clear Guideline 4.2: push notifications, the share sheet, and an offline screen.
- [ ] ADR 0011 records the decision.

### PB-17 Spike: iOS builds on macOS CI · #TBD · 2 pts · P1 · spike · v1.0
- [ ] A GitHub Actions macOS workflow builds and signs the app and uploads it to TestFlight, with the signing secrets in GitHub secrets.

### PB-18 Apple Developer enrollment · #TBD · 1 pt · P1 · chore · v1.0 · owner
- [ ] Decide on an individual or organization (LLC) account after the Phase 3 legal review. Get a D-U-N-S number if it's an organization.
- [ ] Enrolled ($99/year), with the account holder recorded in the README.

### PB-19 App Store listing and review pack · #TBD · 3 pts · P1 · chore · v1.0
- [ ] App Store Connect listing: name, description, icon, 6.7" and 6.5" screenshots, a privacy policy URL, and a support URL.
- [ ] A privacy label covering email, city and state, payment handles, and user content. An age rating that matches the 18+ rule.
- [ ] A demo account and review notes covering link-out gifts (Guideline 3.2.1(vii)), reporting, blocking, and account deletion.
- [ ] User-facing copy says "gift" or "chip in", never "charitable donation".
