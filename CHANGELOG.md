# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Added
- Project foundation: tooling, CI, templates, PRD, ADRs, threat model, and a Flask skeleton with `/health`.
- Render staging blueprint (`render.yaml`) with gunicorn and free Postgres; ADR 0005.
- `User` and `Post` models, Alembic migration 0001, and a `flask seed` command that creates 10 users and 20 posts for local dev (#1). Money is stored as integer cents (ADR 0006).

- Sign up with email verification (#2): CSRF-protected forms (Flask-WTF), hashed passwords, signed 48-hour verification links, a resend option, and a `verified_required` guard. Emails are logged to the console unless `MAIL_SERVER` is set (ADR 0007).
- Mobile-first base layout and stylesheet.

### Changed
- Staging runs `flask db upgrade` before starting gunicorn.
