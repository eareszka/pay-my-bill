# Roadmap: staging to the App Store

**Owner:** Emery · **Last updated:** 2026-10-30

This expands the PRD's "Scope by release" into the steps between today's staging site and an approved iOS app. Each phase ends with a check that has to pass before the next phase starts. Backlog items are in `docs/backlog/product-backlog.md`.

## Phase 1: Finish v0.1-alpha (Sprints 2–5)
The site isn't usable until donations work.
- Sprint 2: payment deep links, donation pledge → recipient confirm or dispute, auto-expiry (PB-4)
- Sprints 3–4: XP, levels, badges, streaks, kudos, leaderboards by people helped (ADR 0009), results updates (PB-1, PB-2)
- Sprint 5: reports and admin queue, user blocking (PB-12), post and account deletion (PB-6), ToS and Privacy (PB-7), PWA manifest and service worker, e2e tests

Reporting, blocking, and in-app account deletion are App Store requirements (Guidelines 1.2 and 5.1.1(v)). They ship in v0.1 so the wrapper doesn't need new features later.

**Done when:** a real pledge goes from post → Cash App/Venmo/PayPal → confirmed, end to end, on a phone against staging.

## Phase 2: Production (v0.2-beta)
- Paid hosting, a custom domain, and HTTPS (PB-13, ADR 0010). The staging Postgres expiry (PB-8) is handled first.
- A transactional email provider so verification emails arrive (PB-14).
- Error monitoring, an uptime check, and database backups (PB-15).
- An admin account and a moderation runbook.

**Done when:** `/health` returns 200 on the production domain, and a new user can sign up, verify by email, and post.

## Phase 3: Closed beta
- 10–30 invited users (PB-11). The owner uses it daily from the home screen.
- Feedback goes into GitHub issues and gets fixed over 1–2 sprints. Watch abuse cases T1–T15.
- A lawyer reviews the ToS and Privacy Policy (a v1.0 gate in the PRD), and the owner decides whether to form an LLC. That choice decides the Apple account type (PB-18).

**Done when:** the beta exit criteria from PB-11 are met, and the legal review is done.

## Phase 4: iOS wrapper (v1.0)
- A Capacitor shell around the production site (PB-16, ADR 0011). Guideline 4.2 rejects thin web wrappers, so it adds native value: push notifications (pledge received, confirm reminders, results update due), the native share sheet, and an offline screen.
- Builds need macOS and Xcode. CI builds and signs on a GitHub Actions macOS runner (PB-17), so no Mac is needed locally.
- Apple Developer Program, $99/year (PB-18). An organization account (LLC) needs a D-U-N-S number and takes a few weeks to set up, so start early.

### Payments and Apple's rules
- Guideline 3.2.1(vii) allows person-to-person gifts outside in-app purchase when the gift is optional and 100% goes to the recipient. Link-out handles (ADR 0002) fit this, so keep them and never take a cut.
- Guideline 3.2.2(iv) limits *charitable* donation collection to registered nonprofits. User-facing copy says "gift" or "chip in", not "donate to charity".
- Sign in with Apple isn't required while login is email and password only (Guideline 4.8).

**Done when:** a TestFlight build installs on the owner's iPhone, and push notifications arrive.

## Phase 5: App Store submission
- Listing, screenshots, privacy label, age rating, a demo account, and review notes (PB-19).
- TestFlight with the beta group, then submit. Expect 1–2 rejection rounds, most likely on 4.2, 1.2, or payment wording.

**Done when:** App Review approves the app.

## Costs
| Item | Cost |
|---|---|
| Apple Developer Program | $99/year |
| Hosting (web + Postgres) | ~$15/month |
| Domain | ~$12/year |
| Email provider | free tier at beta volume |
| LLC and lawyer review | optional, varies by state |
