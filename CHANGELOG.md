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
- Feed of open posts at `/` (#6): newest first, All/Wants/Needs filter, 20 per page, and cards with a kind chip, poster, region, goal, and progress bar. Progress is $0 until confirmed donations arrive in Sprint 2 (ADR 0004).
- Post detail page `/posts/<id>` (#7): story, poster and region, goal, progress, and the poster's payment handles while the post is open. Pending-review and removed posts return 404 to everyone except the owner and admins. Feed cards and new posts link here.

### Changed
- Staging runs `flask db upgrade` before starting gunicorn.
