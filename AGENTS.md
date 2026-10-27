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
4. `docs/threat-model.md`: abuse cases T1–T10 and which sprint mitigates each
5. `docs/backlog/sprint-01.md`: the current sprint's stories and acceptance criteria

## Stack and commands
- Python 3.12, Flask app factory in `app/__init__.py`, blueprints in `app/routes/`
- Planned modules: `app/models.py`, `app/rewards.py`, `app/leaderboard.py`, `app/moderation.py`, `app/payment_links.py`
- Tests live in `tests/unit/`, `tests/integration/` (Flask test client), and `tests/e2e/` (Playwright, from Sprint 4)

```powershell
python -m venv .venv; .\.venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
ruff check . ; ruff format --check . ; mypy ; pytest     # all must pass
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
- Keep code style consistent with the existing code: typed functions, small modules, no unnecessary comments.
- **Secrets:** never commit `.env`. Config comes from environment variables only (see `.env.example`).

## Product rules to enforce in code
- Post `goal_amount` ≤ $1,000. Each user can have at most 2 open posts.
- New posts are checked against the fundraising keyword list (invest, startup, business, equity, seed, LLC, inventory, pre-order, launch, crowdfund, shares, ROI, …). A match sets the post to `pending_review`, and it's hidden from the feed.
- Donations go `pending` → `confirmed` | `disputed`. Only the recipient can confirm.
- Leaderboards only count confirmed donations from verified accounts older than 3 days. Anything over $200/week for one donor→recipient pair is excluded and flagged.
- Region is self-reported city and state. No GPS.
- Every form needs a CSRF token. Passwords are hashed. Logins are rate-limited.

## Current state (2026-10-27)
- **Sprint 0 (foundation)** is nearly done. The repo, tooling, CI, templates, docs, and the `/health` skeleton are finished, and tests pass at 100% coverage.
- The GitHub repo `eareszka/pay-my-bill` (private) exists and has labels. **Waiting on:** the owner running `powershell -File scripts/bootstrap_github.ps1` to push `main` and create the milestones.
- **Remaining Sprint 0 items:**
  - Confirm CI is green on GitHub
  - Create the GitHub Projects board (columns: Backlog → Ready → In Progress → In Review → Done)
  - Create the Sprint 1 stories from `docs/backlog/sprint-01.md` as issues, labelled with `type:story`, `points:N`, `priority:PN`, `epic:*`, and `sprint:01`, under milestone `v0.1-alpha`
  - Deploy `/health` to staging (Fly.io or Render; the owner hasn't chosen yet)
- **Next sprint:** Sprint 1, "Users can sign up and post" (S1-1 … S1-7, 23 points). Start with **S1-7, the data model and migrations**, because the other stories depend on it.

## Coordination
Other agents (Claude Code) may also work in this repo. To avoid conflicts:
- Before starting work, pull `main` and check the open PRs and branches.
- Claim a story by assigning its issue or noting it in the sprint file's daily log.
- Don't rewrite another agent's open branch. Comment on its PR instead.
