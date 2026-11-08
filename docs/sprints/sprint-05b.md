# Sprint 5b: Launch

**Dates:** 2026-11-08 (one night) · **Goal:** real people can sign up, post, and be moderated on the live site

The owner chose to open the site to the public tonight, before anyone else ships the idea. Sprint 5's remaining stories (#79, #80, #81) are paused, and swiping (#91) waits.

## Committed
| Story | Issue | Points | Status |
|---|---|---|---|
| L-1 Terms of Service and Privacy pages | #32 | 2 | Done (#93) |
| L-2 Password reset | #82 | 3 | Done (#94) |
| L-3 Report a post or user, with an admin queue (includes #68) | PB-33 | 5 | Done (#95) |
| L-4 Real email on staging (Brevo HTTPS API) | — | 2 | Done (#96) |

**Total:** 12 points.

## Skipped for speed (owner-approved)
- Each PR gets a `/code-review` at low effort instead of medium.
- New pages reuse existing partials and styles, with no Impeccable pass. A finish review comes after launch.
- Terms and Privacy are drafts, with no lawyer review yet (PB-39).
- Hosting stays on the Render free tier at the staging URL. The free Postgres expires around 2026-11-26 (#33).

## Daily log
- 2026-11-08: Planned the launch sprint with the owner: Gmail SMTP, the free Render URL, PRs and CI kept, and Terms, password reset, and reports in scope. Next: L-1. Blocked: none.
- 2026-11-08: #32 merged (#93) and #82 merged (#94). The low reviews found nothing real: one flagged a lockout gap, but login already maps an email to the username. Did PB-33 with #68 (#95). Its review flagged `PostStatus` as missing from the template, but it's a Jinja global. Blocked: none.
- 2026-11-08: Render's free tier blocks outbound SMTP (ports 25/465/587), so Gmail SMTP can't work. The owner chose to stay free with Brevo's HTTPS API (#96). Follow-ups: other sessions aren't ended on a password reset, and admins have no audit log. Next: the owner sets `BREVO_API_KEY`, `MAIL_FROM`, and `CONTACT_EMAIL` in Render, then runs `flask --app app admin grant` and does the phone run. Blocked: owner config.
