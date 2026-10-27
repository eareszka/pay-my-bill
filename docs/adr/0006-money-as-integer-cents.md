# ADR 0006 — Store money as integer cents

**Status:** Accepted · **Date:** 2026-10-27

## Context
Posts have a goal amount capped at $1,000, and later sprints add donation amounts, post progress, and the $200/week per-pair cap. Floats round badly, and SQLAlchemy's `Numeric` on SQLite (the dev database, ADR 0003) is emulated and warns about lossy `Decimal` handling.

## Decision
All money columns are integers in US cents, named with a `_cents` suffix (`Post.goal_cents`). The $1,000 cap is `MAX_GOAL_CENTS = 100_000` in `app/models.py` and is also a database CHECK constraint. Conversion to and from dollars happens only at the form and template edges.

## Consequences
- Sums and caps are exact and behave the same on SQLite and Postgres.
- Forms must parse dollar input into cents, and templates must format cents as dollars. Both get unit tests when they're built.
