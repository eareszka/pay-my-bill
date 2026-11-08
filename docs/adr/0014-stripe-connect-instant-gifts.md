# ADR 0014: Instant gifts through Stripe Connect

**Status:** Proposed. It supersedes ADR 0002 once Stripe approves the platform. · **Date:** 2026-11-08

## Context
On the first real test (2026-11-08), the owner found link-out giving clunky. The donor leaves for PayPal, sends the amount by hand, comes back, and records it, and then the recipient has to confirm it arrived. The owner wants instant checkout like Kickstarter or Buy Me a Coffee. Cash App, Venmo, and PayPal personal accounts have no API for an app to send person-to-person money or see that it arrived, so instant checkout means a payment processor.

## Decision
Use **Stripe Connect with Express accounts**, after Stripe approves the use case:
- Recipients onboard once through Stripe-hosted onboarding, which handles identity, bank details, and payouts. Pay My Bill never stores bank or card data.
- Donors pay by card, Apple Pay, or Google Pay through Stripe Checkout. Each charge is a destination charge to the recipient's connected account.
- A signed `checkout.session.completed` webhook records the gift as confirmed. A processor-verified payment replaces recipient confirmation for these gifts, and ADR 0004 is amended to say so.
- Pay My Bill takes no platform fee. Recipients get the whole gift less Stripe's processing fee, and the page says so before paying (Apple Guideline 3.2.1(vii), to be checked in PB-9).
- Link-out handles stay as a fallback until Stripe is live, then are reviewed.

## Consequences
- Gifts are instant and verified, with no "I sent it" step and no confirm step.
- Stripe treats crowdfunding as a restricted business, so approval may be refused or need changes. Nothing ships until it's approved.
- The platform carries negative balances from disputes and chargebacks on Express accounts. That needs dispute handling, limits for new donors, and Stripe Radar.
- Fees are about 2.9% + 30¢ per gift, plus a monthly fee per active connected account.
- Recipients may get 1099-Ks. The Terms and Privacy pages need updating before launch, and the LLC and lawyer review (PB-39) move earlier.
- New config: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`. Webhooks must be idempotent.
