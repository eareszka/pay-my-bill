# ADR 0003 — Flask + SQLAlchemy stack

**Status:** Accepted · **Date:** 2026-10-27

## Context
The developer already knows Python and Flask. The app is mostly server-rendered CRUD with a few aggregate queries.

## Decision
Flask with an app factory and blueprints, SQLAlchemy ORM, and Alembic migrations through Flask-Migrate. SQLite in dev; Postgres in staging and prod. Jinja templates with small vanilla JS.

## Consequences
- Simple, testable, and quick to build.
- No SPA framework. If the UI later needs heavy interactivity, revisit this in a new ADR.
