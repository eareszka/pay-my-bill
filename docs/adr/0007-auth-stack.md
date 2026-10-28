# ADR 0007 — Auth stack: sessions, CSRF, email tokens, login throttle, mail backend

**Status:** Accepted · **Date:** 2026-10-28

## Context
Sprint 1 adds sign-up, email verification, log in and out, and payment-handle change notices. The threat model requires hashed passwords and rate-limited logins (T6) and CSRF tokens on every form (T8). Staging runs gunicorn with more than one worker on Render (ADR 0005), and there's no email provider yet.

## Decision
- **Sessions:** Flask-Login with Flask's signed-cookie session. `User` implements the Flask-Login protocol directly instead of subclassing the untyped `UserMixin`, so mypy `--strict` stays clean. `app/auth.py` re-exports a typed `login_required` and adds `verified_required`.
- **Forms and CSRF:** Flask-WTF. `CSRFProtect` is global, so every POST needs a token, including forms that have no fields (`EmptyForm`).
- **Passwords:** `werkzeug.security.generate_password_hash` (scrypt), the same as `seed.py`.
- **Email tokens:** `itsdangerous.URLSafeTimedSerializer` keyed on `SECRET_KEY`, with one salt per purpose (`app/tokens.py`). Verification links expire after 48 hours. No token table is needed.
- **Login throttle:** failed attempts are stored in a `login_attempts` table and counted per account (or per typed identifier when no account matches) over a sliding 15-minute window (added in S1-2). An in-memory limiter such as Flask-Limiter's default storage would be per gunicorn worker and lost on restart. Redis would be a new service for a single check.
- **Mail:** `app/mail.py` sends through the stdlib `smtplib` when `MAIL_SERVER` is set. Otherwise it logs the full message, which is how dev and staging work today: verification links can be read from the console or the Render logs.

## Consequences
- No new infrastructure. Turning on real email later only takes environment variables.
- Until `MAIL_SERVER` is configured, anyone with access to the staging logs can read verification links. That's acceptable for a private staging environment, but production needs SMTP before launch.
- The `login_attempts` table grows over time and needs a periodic cleanup job. That's a backlog item, not in Sprint 1.
