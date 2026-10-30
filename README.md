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
flask --app app run
pytest
```

## Deploy (staging)
Staging: https://pay-my-bill-staging.onrender.com ([`/health`](https://pay-my-bill-staging.onrender.com/health))

Staging runs on [Render](https://render.com) from the [`render.yaml`](render.yaml) Blueprint (see [ADR 0005](docs/adr/0005-render-staging.md)):

- A free Python web service runs `gunicorn "app:create_app()"`, with a health check on `/health`.
- A free Postgres database supplies `DATABASE_URL`. Render generates `SECRET_KEY`.
- On each start, `flask db upgrade` applies any new migrations before gunicorn starts.
- Every push to `main` deploys automatically. There are no manual steps after the first Blueprint sync.

Config comes only from environment variables (see `.env.example`). Never commit secrets.

Free-tier caveats: the service sleeps after about 15 minutes idle, so the first request can take up to a minute. The free database expires 30 days after creation.

### When the free staging database expires
The current database expires around 2026-11-26. Staging data is disposable, so recreating it is fine:

1. In the Render dashboard, delete `pay-my-bill-staging-db`.
2. Open the Blueprint and click **Manual Sync**. Render creates a fresh database from `render.yaml` and reconnects `DATABASE_URL` to the web service.
3. Redeploy the web service. `flask db upgrade` builds the schema on start.
4. Check that [`/health`](https://pay-my-bill-staging.onrender.com/health) returns 200.

To keep the data instead, upgrade the database to a paid plan before it expires.

## Docs
- [Product requirements](docs/PRD.md)
- [Development process](docs/process.md): sprints, Definition of Ready and Done, git workflow
- [Architecture decisions](docs/adr/)
- [Threat model](docs/threat-model.md)
- [Sprint records](docs/sprints/)
