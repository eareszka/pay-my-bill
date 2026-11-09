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

## Amendment (2026-10-28, #23)
SQLAlchemy 2.1 made psycopg 3 the default driver for `postgresql://` URLs, so the psycopg2-only install crashed at boot and every staging deploy after #12 failed. The driver is now `psycopg[binary]` (v3). `create_app` rewrites any Postgres URL scheme to `postgresql+psycopg://`, and SQLAlchemy is pinned to `>=2.1,<2.2` so a future default change can't silently break deploys again. The hosting decision is unchanged.

## Amendment (2026-11-09): database on Neon (#33)
Render's free Postgres is deleted 30 days after creation, which would have lost every account and post around 2026-11-26. The owner chose a no-cost fix: the database moved to Neon's free tier (AWS us-west-2, beside Render's Oregon region), which doesn't expire. The web service still runs on Render, and `DATABASE_URL` is now a dashboard secret instead of a link to a Render database. The data was copied table by table and the row counts were checked to match, at Alembic revision 0012. Neon's free tier caps storage at 0.5 GB and suspends compute when idle, so the first query after a quiet spell is a little slower.
