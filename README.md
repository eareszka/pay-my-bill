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
flask --app app run
pytest
```

## Docs
- [Product requirements](docs/PRD.md)
- [Development process](docs/process.md): sprints, Definition of Ready and Done, git workflow
- [Architecture decisions](docs/adr/)
- [Threat model](docs/threat-model.md)
- [Sprint records](docs/sprints/)
