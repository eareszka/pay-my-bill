# Pay My Bill

A community app where people post everyday wants and needs, like "need help with rent" or "want the new Zelda", and others chip in through Cash App, Venmo, or PayPal. Donors earn XP, badges, streaks, and leaderboard spots, and get thank-yous from the people they helped.

**Business, startup, and investment fundraising is prohibited.**

## Quick start
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
pre-commit install
cp .env.example .env
flask --app app db upgrade      # create or upgrade the local SQLite DB
flask --app app seed            # optional: 10 fake users + 20 posts (password: password123)
flask --app app demo seed       # live site only for phone testing: 16 labeled test wants (demo clear removes them)
flask --app app run
pytest
```

## Deploy (staging)
Staging: https://yearnly.app ([`/health`](https://yearnly.app/health)), also reachable at https://pay-my-bill-staging.onrender.com

Staging runs on [Render](https://render.com) from the [`render.yaml`](render.yaml) Blueprint (see [ADR 0005](docs/adr/0005-render-staging.md)):

- A free Python web service runs `gunicorn "app:create_app()"`, with a health check on `/health`.
- A free Postgres database supplies `DATABASE_URL`. Render generates `SECRET_KEY`.
- On each start, `flask db upgrade` applies any new migrations before gunicorn starts.
- Every push to `main` deploys automatically. There are no manual steps after the first Blueprint sync.

Daily jobs run from GitHub Actions (`.github/workflows/daily-jobs.yml`, 15:00 UTC, #258). `flask --app app gifts remind` emails posters about gifts waiting 3 or more days to be confirmed. They need the `DATABASE_URL` (Neon's direct connection string) and `BREVO_API_KEY` repository secrets, and they skip with a warning until both are set. Run them early from Actions → Daily jobs → Run workflow.

`flask --app app posts remind` emails posters on day 3 and day 6 of their 7-day results update deadline, once each. It runs in the same workflow, followed by `flask --app app auth prune`, which deletes login and email throttle rows older than a week (#15). Then `flask --app app posts retry-photos` retries photo deletes that failed (#149). That one needs the R2 secrets (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `R2_PUBLIC_URL`) and otherwise skips.

Config comes only from environment variables (see `.env.example`). Never commit secrets.

Free-tier caveats: the service sleeps after about 15 minutes idle, so the first request can take up to a minute. The free database expires 30 days after creation.

### When the free staging database expires
The current database expires around 2026-11-26. Staging data is disposable, so recreating it is fine:

1. In the Render dashboard, delete `pay-my-bill-staging-db`.
2. Open the Blueprint and click **Manual Sync**. Render creates a fresh database from `render.yaml` and reconnects `DATABASE_URL` to the web service.
3. Redeploy the web service. `flask db upgrade` builds the schema on start.
4. Check that [`/health`](https://yearnly.app/health) returns 200.

To keep the data instead, upgrade the database to a paid plan before it expires.

## Monitoring and backups (#259)
- **Errors:** set `SENTRY_DSN` in the Render dashboard (Sentry free tier, a Flask project). Unhandled errors outside development are reported without request bodies, cookies, headers, query strings, users, or the tokens in `/verify`, `/reset`, and `/gifts/answer` links (`app/monitoring.py`). Outside development, database errors also hide row values (`hide_parameters`). With no DSN set, nothing is sent.
- **Uptime:** in [UptimeRobot](https://uptimerobot.com) (free), add an HTTP(s) monitor for `https://yearnly.app/health` every 5 minutes, alerting the owner's email. It also keeps the free Render service from sleeping (one service running all month fits the 750 free hours).
- **Backups:** Neon keeps a point-in-time history of the database. Its length depends on the plan, so check it under **Settings → Storage → History retention**. To restore:
  1. In the Neon console, open the project → **Branches** → **Create branch**, and pick **Past data** at the time to go back to.
  2. Copy the new branch's direct connection string. Run `DATABASE_URL=<it> flask --app app db current` and confirm it prints the latest revision.
  3. To switch over, set Render's `DATABASE_URL` (and the `DATABASE_URL` GitHub secret) to the branch, or restore the main branch in place with **Restore**.
  4. Check that [`/health`](https://yearnly.app/health) returns 200.

  Test a restore once with a throwaway branch, then note the date here. Last tested: not yet.

## Docs
- [Product requirements](docs/PRD.md)
- [Development process](docs/process.md): sprints, Definition of Ready and Done, git workflow
- [Architecture decisions](docs/adr/)
- [Threat model](docs/threat-model.md)
- [Sprint records](docs/sprints/)
