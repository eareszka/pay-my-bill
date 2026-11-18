# AGENTS.md — Instructions for AI coding agents (Codex, Claude, etc.)

Read this file fully before making any change. The project is run as a professional Scrum project: **process is part of the deliverable.**

## What this project is
**Pay My Bill** is a mobile-first web PWA. People post everyday wants and needs (for example "need help with rent" or "want a new video game", capped at $1,000), and other users chip in through the poster's **Cash App, Venmo, or PayPal handle**. The app **never holds or processes money**. Donors are rewarded with XP and levels, badges, weekly streaks, kudos, global/state/city leaderboards, and thank-you posts from recipients.

**Hard rule: business, startup, product, or investment fundraising is prohibited.** Never build features that facilitate it.

## Agents
The owner runs one Claude Code session per role and tells each session its role when it starts. GitHub labels mark each lane, so you can find your own work with `gh issue list -l agent:<role>`.

| Role | Owns | Never |
|---|---|---|
| **main** | `agent:main` issues: models, migrations, routes, business rules, tests, and plain working templates for new screens | Impeccable design work |
| **ui** | `agent:ui` issues: Impeccable design, the look and motion in templates, CSS, and JS, and finish reviews | Models, migrations, or business rules |
| **todo** | Turns each of the owner's testing notes into a GitHub issue: a short title, what happened, and where (page, device). No lane label | Code or branches |
| **coordinator** | Triage of unlabeled issues (lane, type, priority), sprint planning with the owner, keeping this file and the sprint file short, `/code-review` on PRs | Feature code |

- **Full-stack stories:** main owns the branch, builds the working version with tests, and comments `ready for ui` on the PR. ui adds design commits on the same branch and comments `ui done`. main merges once CI is green and the owner approves. Only the agent named in the latest handoff comment pushes to the branch.
- **Before starting:** pull `main`, then check open PRs and your label. Don't touch another agent's branch unless it was handed to you. Comment on its PR instead.
- **Status lives in GitHub and the sprint file, not here.** This file holds rules and lasting facts only. Untriaged issues: `gh issue list --search "-label:agent:main -label:agent:ui"`.

## Reading by role
- **Everyone:** this file, `docs/process.md`, and the current sprint, `docs/sprints/sprint-06.md` (acceptance criteria are in the `docs/backlog/` file it links).
- **main:** `docs/PRD.md`, `docs/threat-model.md` (abuse cases and their mitigations), and `docs/adr/`. **Don't reverse an ADR without writing a new one.** Each file's Status line says whether it's current:
   - 0001: web PWA, not native · 0003: Flask + SQLAlchemy + Jinja/vanilla JS (no SPA framework) · 0005: Render for staging
   - 0002: link-out payments (Cash App, Venmo, PayPal). 0014 and 0016: card gifts through Stripe Connect with a 1% fee (0014 is Proposed until Stripe approves the platform)
   - 0004: **only recipient-confirmed donations count** toward XP, badges, streaks, leaderboards, and post progress
   - 0006: money is integer cents · 0010: XP per person helped (amount-blind) · 0013: the top of the board rewards follow-through
   - 0015: post photos in R2 · 0017: the product name is Yearnly
- **ui:** `PRODUCT.md`, `DESIGN.md`, and the `.impeccable/surfaces/` brief for the screen you're working on.
- **coordinator:** `docs/backlog/product-backlog.md`, `docs/roadmap.md`, and `docs/sprints/velocity.md`.

## Stack and commands
- Python 3.12, Flask app factory in `app/__init__.py`, blueprints in `app/routes/`
- Models live in `app/models.py` and subclass `Base` from `app/extensions.py` (not `db.Model`, which mypy can't type). Migrations live in `migrations/` (`flask --app app db migrate -m "..."`). Money is integer cents (ADR 0006).
- `app/rewards.py` computes XP, levels, streaks, and badges from confirmed gifts (ADR 0010). Other key modules: `app/auth.py` (typed `login_required`, `verified_required`, and the login throttle), `app/leaderboard.py`, `app/moderation.py`, `app/money.py` (dollars ↔ cents), `app/payment_links.py`, `app/mail.py` (Brevo when `BREVO_API_KEY` is set, otherwise SMTP or the console), and `app/security.py`.
- Testing gotchas: use `tests.conftest.login_as` and the `make_user` fixture. Requests made inside an already-pushed app context share `g`, so build test apps outside it. `migrations/env.py` keeps existing loggers enabled.
- Deploys install exact, hash-checked versions from `requirements.lock` (#177). After changing dependencies in `pyproject.toml`, regenerate it with `uv pip compile pyproject.toml --python-version 3.12 --python-platform x86_64-unknown-linux-gnu --generate-hashes --no-header -o requirements.lock`, run the tests, and commit both.
- Tests live in `tests/unit/`, `tests/integration/` (Flask test client), and `tests/e2e/` (Playwright, #207). The e2e tests are skipped by default. Run them with `python -m playwright install chromium` once, then `pytest -m e2e --no-cov` and `python -m tests.e2e.report`. Screenshots and `findings.md` land in `tests/e2e/artifacts/` (gitignored). Design findings go to Impeccable for the fix.

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
- **Update the sprint record** in `docs/sprints/sprint-NN.md`: add **one** daily-log line of 200 characters or less (what you did, what's next, and any blockers), and update the story status. Details go in the PR description.
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

## Environments and ops
- **`main` is protected:** changes only land through a PR, the `checks` CI job must pass with the branch up to date, and force-pushes and deletion are blocked, admins included. Merged branches delete themselves. The repo is public, so never commit secrets (gitleaks runs in pre-commit).
- **Projects board:** https://github.com/users/eareszka/projects/4, with columns Backlog → Ready → In Progress → In Review → Done.
- **Staging is live** on Render at https://yearnly.app (ADR 0005 and 0017, `render.yaml`; the onrender.com address still works) and auto-deploys from `main`. DNS lives in Cloudflare: an A record for `@` and a `www` CNAME to Render, grey-clouded, plus Email Routing (`support@` forwards to the owner) and Brevo's DKIM, DMARC, and `em.` tracking records. Mail goes out as `Yearnly <no-reply@yearnly.app>` through Brevo's HTTPS API, because Render's free tier blocks SMTP. The database is Neon's free Postgres, with `DATABASE_URL` set in the Render dashboard (#33).
- **Admin:** `flask --app app admin grant <email>` / `admin revoke <email>`; the queue is at `/admin`. Results-update reminders: `flask --app app posts remind`.
- **iOS shell (#193):** `mobile/` is a Capacitor 8 project (`app.yearnly.ios`) that loads https://yearnly.app. Ship with Actions → **iOS TestFlight** (secrets `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_KEY_P8`, `APPLE_TEAM_ID`). After changing `capacitor.config.json`, run `npx cap sync ios` in `mobile/` and commit `ios/`.
