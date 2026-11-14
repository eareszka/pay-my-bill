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
- 2026-11-08: Real gifts work on staging. The owner found link-out clunky and wants instant checkout, and chose to apply to Stripe Connect first and build once approved. ADR 0014 (proposed), PB-41 to PB-43, and #98 (streamline chip-in) were added. Venmo links were fixed (#97). Next: one-tap confirm from the gift email while Stripe reviews. Blocked: Stripe approval.
- 2026-11-13: The owner wants to try the app on an iPhone outside the browser, then on TestFlight. Did #185: a manifest, icons, iOS Home Screen meta, and an offline page from a service worker. Checked in Chrome that the worker registers and that the offline page shows with the server stopped. Next: the Capacitor shell and a GitHub Actions build to TestFlight. Blocked: none.
- 2026-11-14: The owner named the product Yearnly (ADR 0017, #35) after checks on Chip In, Chip Along, Penny Wish, Upswing, and others. Next: the owner buys yearnly.app and getyearnly.com at Cloudflare, then email, the custom domain, and the rename story in Sprint 6. Blocked: none.
- 2026-11-09: #14 merged (#115): three verification emails an hour per account. The owner asked for posts on profiles with edit and delete (#116). The owner chose: everyone sees the list, every field can be edited until the first gift and only the story after it, and an "Edited" date is shown. Next: Stripe live once the ID review clears. Blocked: Stripe ID review.
