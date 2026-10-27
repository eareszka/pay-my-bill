# ADR 0005 — Render for staging

**Status:** Accepted · **Date:** 2026-10-27

## Context
Sprint 0 needs a staging environment that serves `/health`, runs Postgres (ADR 0003), and auto-deploys from `main`. The candidates were Fly.io and Render. This is a solo student project with no hosting budget.

## Decision
Render, defined as code in `render.yaml` (a Blueprint): one free Python web service running gunicorn and one free Postgres database. Config comes only from environment variables. Render generates `SECRET_KEY` and injects `DATABASE_URL` from the database.

Render was chosen over Fly.io because:
- Its free tier includes managed Postgres and git-push auto-deploys without a CLI, Dockerfile, or payment card.
- The whole environment is reviewable in one YAML file in the repo.
- There's less operational surface (no machines, volumes, or regions to manage).

## Consequences
- Free web services sleep after about 15 minutes idle, and the first request after that takes up to a minute. That's fine for staging, not for prod.
- Free Postgres databases expire 30 days after creation. Recreate the database or upgrade the plan before then, and keep no data worth losing on staging.
- `psycopg2-binary` and `gunicorn` become runtime dependencies.
- Revisit hosting for prod at v0.2-beta in a new ADR.
