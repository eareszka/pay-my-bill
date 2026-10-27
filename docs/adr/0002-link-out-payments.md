# ADR 0002 — Link-out payments instead of in-app processing

**Status:** Accepted · **Date:** 2026-10-27

## Context
Moving money between users in-app (for example through Stripe Connect) brings KYC onboarding, money-transmitter considerations, fees, chargebacks, and a lot of compliance work.

## Decision
Posters list their Cash App, Venmo, and/or PayPal handles. Donors pay through those apps via deep links. The app never holds or processes funds.

## Consequences
- No licensing or KYC burden, and much faster to build.
- Donations can't be verified automatically, so verification falls to the recipient (see ADR 0004).
- Deep-link formats are third-party and may change. They are isolated in `app/payment_links.py`.
