# AGENTS.md — Instructions for AI coding agents (Codex, Claude, etc.)

Read this file fully before making any change. The project is run as a professional Scrum project: **process is part of the deliverable.**

## What this project is
**Pay My Bill** is a mobile-first web PWA. People post everyday wants and needs (for example "need help with rent" or "want a new video game", capped at $1,000), and other users chip in through the poster's **Cash App, Venmo, or PayPal handle**. The app **never holds or processes money**. Donors are rewarded with XP and levels, badges, weekly streaks, kudos, global/state/city leaderboards, and thank-you posts from recipients.

**Hard rule: business, startup, product, or investment fundraising is prohibited.** Never build features that facilitate it.

## Required reading (in order)
1. `docs/PRD.md`: goals, non-goals, scope by release, risk register
2. `docs/process.md`: sprint cadence, Definition of Ready and Done, git workflow
3. `docs/adr/`: decisions already made. **Don't reverse them without writing a new ADR.**
   - 0001: web PWA, not native
   - 0002: link-out payments only (no Stripe or in-app money)
   - 0003: Flask + SQLAlchemy + Jinja/vanilla JS (no SPA framework)
   - 0004: **only recipient-confirmed donations count** toward XP, badges, streaks, leaderboards, and post progress
   - 0005: Render for staging (`render.yaml`)
   - 0006: money is stored as integer cents
   - 0010: XP per person helped (amount-blind)
   - 0013: the top of the board rewards follow-through
4. `docs/threat-model.md`: abuse cases T1–T10 and which sprint mitigates each
5. `docs/backlog/sprint-05.md`: the current sprint's stories and acceptance criteria

## Stack and commands
- Python 3.12, Flask app factory in `app/__init__.py`, blueprints in `app/routes/`
- Models live in `app/models.py` and subclass `Base` from `app/extensions.py` (not `db.Model`, which mypy can't type). Migrations live in `migrations/` (`flask --app app db migrate -m "..."`). Money is integer cents (ADR 0006).
- `app/rewards.py` computes XP, levels, streaks, and badges from confirmed gifts (ADR 0010). Planned: `app/leaderboard.py` (`app/moderation.py` and `app/payment_links.py` exist now)
- Deploys install exact, hash-checked versions from `requirements.lock` (#177). After changing dependencies in `pyproject.toml`, regenerate it with `uv pip compile pyproject.toml --python-version 3.12 --python-platform x86_64-unknown-linux-gnu --generate-hashes --no-header -o requirements.lock`, run the tests, and commit both.
- Tests live in `tests/unit/`, `tests/integration/` (Flask test client), and `tests/e2e/` (Playwright, from Sprint 4)

```powershell
python -m venv .venv; .\.venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
ruff check . ; ruff format --check . ; mypy ; pytest     # all must pass
flask --app app db upgrade ; flask --app app seed      # local dev DB + fake data
flask --app app run
```

## Workflow rules (non-negotiable)
- **Never commit directly to `main`.** Create a branch named `feat/<issue#>-short-name`, `fix/<issue#>-…`, or `chore/<issue#>-…`, then open a PR using `.github/pull_request_template.md`.
- **Conventional Commits:** `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`. Reference the issue (`Closes #N`).
- **One story per PR.** Work only on stories in the current sprint backlog. New ideas go into the backlog, not into the current PR.
- **Definition of Done for each PR:**
  - CI is green: ruff, mypy `--strict`, pytest with ≥80% coverage, pip-audit
  - New logic has tests
  - Every acceptance criterion is met
  - CHANGELOG `[Unreleased]` is updated
  - An ADR is added for any architectural decision
- **Update the sprint record** in `docs/sprints/sprint-NN.md`: add a daily-log line with what you did, what's next, and any blockers, and update the story status.
- **Frontend design uses the Impeccable skill** (the owner requires it; `npx impeccable install` sets it up for Claude Code, Codex, or Cursor). `PRODUCT.md` holds the product context, and `.impeccable/surfaces/` holds each screen's brief. Ask the owner before deciding user stories, backend approach, or how the frontend looks.
- Keep code style consistent with the existing code: typed functions, small modules, no unnecessary comments.
- **Secrets:** never commit `.env`. Config comes from environment variables only (see `.env.example`).

## Product rules to enforce in code
- Post `goal_cents` ≤ 100,000 ($1,000; `MAX_GOAL_CENTS`, also a DB CHECK). Each user can have at most 2 open posts.
- New posts are checked against the fundraising keyword list (invest, startup, business, equity, seed, LLC, inventory, pre-order, launch, crowdfund, shares, ROI, …). A match sets the post to `pending_review`, and it's hidden from the feed.
- Donations go `pending` → `confirmed` | `disputed`. Only the recipient can confirm.
- Leaderboards only count confirmed donations from verified accounts older than 3 days. Anything over $200/week for one donor→recipient pair is excluded and flagged.
- Leaderboards rank by **distinct recipients helped**, never by dollars (ADR 0009).
- A post that closes with any confirmed donation owes a **results update** within 7 days of the later of the close and the latest confirmation (note ≥ 20 chars, text only, never a required receipt). Open posts close on their own after 30 days. While one is overdue, that user can't create posts (ADR 0008).
- `pending` donations auto-expire after 14 days with no credit (T15). Users must attest they're 18+ at signup (T13).
- The feed shows one ticket at a time, and the first ticket rewards follow-through: overdue posters are out, a good record comes first, then first-time posters, then closest to goal (ADR 0013).
- Region is self-reported city and state. No GPS.
- Every form needs a CSRF token. Passwords are hashed. Logins are rate-limited.

## Current state (2026-10-28)
- **Sprint 0 (foundation)** is done. The repo, tooling, CI, templates, docs, the `/health` skeleton, and staging are finished, and tests pass at 100% coverage.
- The public GitHub repo `eareszka/pay-my-bill` is pushed, CI is green, and the labels and milestones (v0.1-alpha, v0.2-beta, v1.0) exist.
- **Projects board:** https://github.com/users/eareszka/projects/4, with columns Backlog → Ready → In Progress → In Review → Done. Move cards as work progresses.
- **`main` is protected:** changes only land through a PR, the `checks` CI job must pass with the branch up to date, and force-pushes and deletion are blocked, admins included. The repo is public, so never commit secrets (gitleaks runs in pre-commit).
- **Staging is live** on Render at https://yearnly.app (ADR 0005 and 0017, `render.yaml`; the onrender.com address still works). DNS lives in Cloudflare: an A record for `@` and a `www` CNAME to Render, grey-clouded, plus Email Routing (`support@` forwards to the owner) and Brevo's DKIM, DMARC, and `em.` tracking records. Mail goes out as `Yearnly <no-reply@yearnly.app>`. It auto-deploys from `main`. The database is Neon's free Postgres (it doesn't expire), with `DATABASE_URL` set in the Render dashboard (ADR 0005 amendment, #33).
- The Sprint 0 Review and Retro are left for the owner to write on Sunday.
- **Sprint 1, "Users can sign up and post"** is done: issues #1–#7 (23 points) merged through PRs #12, #13, #16–#20. The app has sign-up with email verification, log in and out with a DB-backed lockout (migration 0002, ADR 0007), a profile with region and payment handles, post creation with the $1,000 cap, 2 open posts, Community Rules, and the fundraising keyword flag, a feed, and post detail pages. Tests: 199, 100% coverage.
- Key modules: `app/auth.py` (typed `login_required`, `verified_required`, login throttle), `app/mail.py` (console unless `MAIL_SERVER` is set), `app/tokens.py`, `app/moderation.py`, `app/money.py` (dollars ↔ cents), `app/payment_links.py` (handle normalization; Sprint 2 adds deep links), and `app/regions.py`. Templates live in `app/templates/` and use `_field.html` and `posts/_meta.html`/`_progress.html` partials.
- Testing gotchas: use `tests.conftest.login_as` and the `make_user` fixture. Requests made inside an already-pushed app context share `g`, so build test apps outside it. `migrations/env.py` keeps existing loggers enabled. Headless Edge can't go below a 492px viewport, so check 360px by rendering pages inside 360px iframes.
- **Backlog follow-ups from reviews:** #14 resend cooldown, #15 async mail + `login_attempts` pruning, #21 keep a handle while a post is open. Payment deep links, donations, and confirmation belong to Sprint 2.
- **Roadmap:** `docs/roadmap.md` lists the phases from staging to App Store approval. PB-12 to PB-19 in the backlog cover the App Store requirements.
- **Product backlog:** `docs/backlog/product-backlog.md` lists the stories and spikes from ADRs 0008/0009 and threat-model cases T11–T15, each with a GitHub issue. Pull from it at Sprint Planning.

- **Sprint 4, "Follow-through"** is done: issues #65, #26, #27, #64, and #28 (16 points) merged through PRs #66, #70, #71, #72, and #74. Posts close by hand or on their own at 30 days (`Post.is_open`, `open_posts()`), and results updates, the overdue block, and the follow-through stat all come from dates when read. Reminders run through `flask --app app posts remind`. Migrations 0006–0009. Rules are in the ADR 0008 amendments.

- **Sprint 5b, "Launch"** (2026-11-08): Terms and Privacy (#93), password reset (#94), reports and the admin queue at `/admin` (#95, migration 0010, `app/routes/admin.py` and `app/routes/reports.py`), and Brevo email (#96). Mail goes through Brevo's HTTPS API when `BREVO_API_KEY` is set, because Render's free tier blocks SMTP. Make an admin with `flask --app app admin grant <email>` and remove one with `admin revoke <email>`; /admin lists recent admin actions. Sprint 5's #79, #80, and #81 are paused.

## Coordination
Other agents (Claude Code) may also work in this repo. To avoid conflicts:
- Before starting work, pull `main` and check the open PRs and branches.
- Claim a story by assigning its issue or noting it in the sprint file's daily log.
- Don't rewrite another agent's open branch. Comment on its PR instead.
