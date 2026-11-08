# Roadmap: staging to the App Store

**Owner:** Emery · **Last updated:** 2026-11-04

This expands the PRD's "Scope by release" into the steps between today's staging site and an approved iOS app. Each phase ends with a check that has to pass before the next phase starts. Backlog items are in `docs/backlog/product-backlog.md`.

## The concept (owner, 2026-11-04)
People pitch in on random people's financial requests. Donors and recipients both have a reason to take part: donors earn visible rewards and perks, and recipients who update and thank people rise in the stack. The app is simple to navigate, and a request is obvious at a glance. Local area isn't a feature for now. The owner chose web first, then the App Store.

## Phase 1: Finish Sprint 5
- Swipe through the pile (#90), once the owner approves the feel.
- Trust information (#79), visible rewards (#80), clear disputes (#81), password reset (#82).
- Recreate the staging Postgres before 2026-11-26 (PB-8).

**Done when:** a real pledge goes from post → Cash App/Venmo/PayPal → confirmed, end to end, on a phone against staging.

## Phase 2: Match the concept (Sprint 6)
Rank the whole stack (PB-27), remove local area (PB-28), show donor rewards at the right moment (PB-29), perks that unlock (PB-30), one-tap thank you (PB-31), simple navigation and clear tickets (PB-32).

**Done when:** a new visitor can tell what a person is asking for and chip in without help, and the stack order follows updates, kudos, thanks, and closeness to goal.

## Phase 3: Safe to open (Sprint 7)
Reports and an admin queue (PB-33, PB-22, PB-23), blocking (PB-12), Terms and Privacy drafts (PB-7), payment-app terms (PB-9). Reporting, blocking, and in-app account deletion are App Store requirements (Guidelines 1.2 and 5.1.1(v)), so they ship before the wrapper.

**Done when:** a reported post can be removed by an admin, a flagged post can be approved, and a blocked person disappears from the feed.

## Phase 4: Production (Sprint 8, v0.2-beta)
- Name and domain (PB-10), which needs the owner.
- Paid hosting, a custom domain, and HTTPS (PB-13, ADR 0011), with real prices brought to the owner first.
- Production settings and security headers (PB-34).
- A transactional email provider (PB-14), sending off the request path (#15), with resend limits (#14).
- Scheduled reminder jobs (PB-35), monitoring and backups (PB-15), an admin account and a moderation runbook.
- An installable web app (PB-36) and browser tests (PB-37).

**Done when:** `/health` returns 200 on the production domain, and a new user can sign up, verify by email, post, and receive a confirmed gift on a phone.

## Phase 5: Closed beta
- 10–30 invited users (PB-11, PB-38). The owner uses it daily from the home screen.
- Feedback goes into GitHub issues and gets fixed over 1–2 sprints. Watch the abuse cases in the threat model.
- A lawyer reviews the ToS and Privacy Policy (PB-39, a v1.0 gate in the PRD), and the owner decides whether to form an LLC. That choice decides the Apple account type (PB-18).
- Decide on rotating older posts (PB-25) and photos (PB-40, PB-20) from what the beta shows.

**Done when:** the beta exit criteria from PB-11 are met, and the legal review is done.

## Phase 6: iOS wrapper (v1.0)
- A Capacitor shell around the production site (PB-16, ADR 0012, which has to supersede ADR 0001's web-only choice). Guideline 4.2 rejects thin web wrappers, so it adds native value: push notifications (pledge received, confirm reminders, results update due), the native share sheet, and an offline screen.
- Builds need macOS and Xcode. CI builds and signs on a GitHub Actions macOS runner (PB-17), so no Mac is needed locally.
- Apple Developer Program, $99/year (PB-18). An organization account (LLC) needs a D-U-N-S number and takes a few weeks to set up, so start early.

### Payments and Apple's rules
- Guideline 3.2.1(vii) allows person-to-person gifts outside in-app purchase when the gift is optional and 100% goes to the recipient. Link-out handles (ADR 0002) fit this, so keep them and never take a cut.
- Guideline 3.2.2(iv) limits *charitable* donation collection to registered nonprofits. User-facing copy says "gift" or "chip in", not "donate to charity".
- Sign in with Apple isn't required while login is email and password only (Guideline 4.8).

**Done when:** a TestFlight build installs on the owner's iPhone, and push notifications arrive.

## Phase 7: App Store submission
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
