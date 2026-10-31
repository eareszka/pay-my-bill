# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Added
- Project foundation: tooling, CI, templates, PRD, ADRs, threat model, and a Flask skeleton with `/health`.
- Render staging blueprint (`render.yaml`) with gunicorn and free Postgres; ADR 0005.
- `User` and `Post` models, Alembic migration 0001, and a `flask seed` command that creates 10 users and 20 posts for local dev (#1). Money is stored as integer cents (ADR 0006).

- Sign up with email verification (#2): CSRF-protected forms (Flask-WTF), hashed passwords, signed 48-hour verification links, a resend option, and a `verified_required` guard. Emails are logged to the console unless `MAIL_SERVER` is set (ADR 0007).
- Mobile-first base layout and stylesheet.
- Log in and log out (#3). More than five failed logins for one account from one IP, or twenty from one IP overall, within 15 minutes returns 429. Attempts are stored in a new `login_attempts` table (migration 0002), and `next` redirects must be local.
- Profile (#4): self-reported city and state (no GPS), plus Cash App, Venmo, and PayPal handles, validated and normalized in `app/payment_links.py`. Changing a handle emails a notice to the account. Public profile at `/u/<username>`.
- Create a post (#5): a Want or Need with a goal up to $1,000 (parsed to cents in `app/money.py`), at most 2 open or in-review posts per user, a payment handle required, and Community Rules (`/rules`) accepted before the first post. Text matching the fundraising keyword list (`app/moderation.py`) goes to `pending_review`.
- Feed of open posts at `/` (#6): newest first, All/Wants/Needs filter, 20 per page, and cards with a kind chip, poster, region, goal, and progress bar. Progress counts confirmed gifts only (ADR 0004).
- Post detail page `/posts/<id>` (#7): story, poster and region, goal, progress, and the poster's payment handles while the post is open. Pending-review and removed posts return 404 to everyone except the owner and admins. Feed cards and new posts link here.

- ADR 0008 (required results updates) and ADR 0009 (leaderboards rank by people helped), threat-model cases T11–T15, new PRD risks and metric, and a product backlog with issues #26–#36 (#25).
- Release roadmap from staging to the App Store (`docs/roadmap.md`) and backlog items PB-12 to PB-19 for the App Store requirements.

- `Donation` model and migration 0003 (#46): a gift's post, donor, amount in cents (capped at $1,000), payment app, and status (`pending`, `confirmed`, `disputed`). Post progress now sums confirmed gifts only (ADR 0004), and `flask seed` adds a few gifts.

- Pay-app buttons on open posts (#43): type an amount once and the Cash App, Venmo, and PayPal buttons open prefilled (`app/static/js/chip-in.js`). Without JS they open the poster's page in each app. Only the poster's apps are shown.

- Record a gift (#45): on an open post, a verified donor who isn't the poster can say "I sent $X via <app>". This saves a `pending` gift and emails the poster. Logged-out visitors get a log-in link. Pending gifts don't move the progress bar until the poster confirms them. A gift can be at most the post's goal, the donor must pick the app they used (tapping an app's pay button picks it), and each donor can have one pending gift per post. Pressing Enter in the amount box doesn't record a gift.
- Confirm or dispute gifts (#44): `/gifts` lists gifts waiting for the poster, each showing its amount, app, donor, post, and date, with Confirm or "Didn't get it". Disputing asks once inline (`?dispute=<id>`, no JavaScript) before acting. The page also lists the gifts you sent with plain statuses: Waiting, Confirmed, Not received. Only the recipient can resolve a gift, and confirming enough to reach the goal marks the post funded. The top bar shows how many gifts are waiting, and long usernames truncate.
- Pending gifts expire after 14 days (#29, T15). That's worked out from the gift's date, with no cron: an expired gift leaves "To confirm" and the badge, can't be confirmed, earns nothing, shows as Expired in "My gifts", and no longer blocks the donor from recording a new gift. `flask gifts remind` emails each poster once about gifts waiting 3 or more days (migration 0004 adds `donations.reminded_at`). Production will run it daily; links use the new `APP_URL` setting.
- 18+ attestation at signup (#30, T13): a required "I'm 18 or older" checkbox. Without it no account is created, and the time it was ticked is stored in `users.adult_attested_at` (migration 0005).
- Design context for Impeccable: `PRODUCT.md` (product truth for design work) and the `/gifts` surface brief in `.impeccable/surfaces/`.

### Fixed
- Staging deploys failing since #12 (#23): SQLAlchemy 2.1 defaults `postgresql://` to psycopg 3, but only psycopg2 was installed. The app now depends on `psycopg[binary]` and pins `postgresql+psycopg://` for any Postgres URL scheme.

### Changed
- CSRF tokens last for the browser session instead of one hour, because donors leave for their payment app in the middle of the form (#45).
- README: steps for recreating the staging database before the free tier expires (#33).
- Staging runs `flask db upgrade` before starting gunicorn.
