# ADR 0014: Instant gifts through Stripe Connect

**Status:** Proposed. It supersedes ADR 0002 once Stripe approves the platform. · **Date:** 2026-11-08

## Context
On the first real test (2026-11-08), the owner found link-out giving clunky. The donor leaves for PayPal, sends the amount by hand, comes back, and records it, and then the recipient has to confirm it arrived. The owner wants instant checkout like Kickstarter or Buy Me a Coffee. Cash App, Venmo, and PayPal personal accounts have no API for an app to send person-to-person money or see that it arrived, so instant checkout means a payment processor.

## Decision
Use **Stripe Connect with Express accounts**, after Stripe approves the use case:
- Recipients onboard once through Stripe-hosted onboarding, which handles identity, bank details, and payouts. Pay My Bill never stores bank or card data.
- Donors pay by card, Apple Pay, or Google Pay through Stripe Checkout. Each charge is a destination charge to the recipient's connected account.
- A signed `checkout.session.completed` webhook records the gift as confirmed. A processor-verified payment replaces recipient confirmation for these gifts, and ADR 0004 is amended to say so.
- *(Superseded by ADR 0016: donors pay a flat amount, fees come out of the gift, and Pay My Bill takes 1%.)* Pay My Bill takes no platform fee. Recipients get the whole gift less Stripe's processing fee, and the page says so before paying (Apple Guideline 3.2.1(vii), to be checked in PB-9).
- Link-out handles stay as a fallback until Stripe is live, then are reviewed.

## Consequences
- Gifts are instant and verified, with no "I sent it" step and no confirm step.
- Stripe treats crowdfunding as a restricted business, so approval may be refused or need changes. Nothing ships until it's approved.
- The platform carries negative balances from disputes and chargebacks on Express accounts. That needs dispute handling, limits for new donors, and Stripe Radar.
- Fees are about 2.9% + 30¢ per gift, plus a monthly fee per active connected account.
- Recipients may get 1099-Ks. The Terms and Privacy pages need updating before launch, and the LLC and lawyer review (PB-39) move earlier.
- New config: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`. Webhooks must be idempotent.

## Amendment (2026-11-09): Managed Risk, direct charges, Accounts v2
Stripe test mode refused the original design. New platforms must create connected accounts with **Accounts v2**, and Express accounts with the platform liable for losses need a loss-liability review. The owner chose to have **Stripe cover losses (Managed Risk)**:
- Accounts are created with `POST /v2/core/accounts`: `dashboard: express`, `defaults.responsibilities.fees_collector` and `losses_collector` both `stripe`, and the `card_payments` merchant capability. Express dashboards with Managed Risk are a public preview, so account creation pins `Stripe-Version: 2026-10-28.preview`. Onboarding uses v2 account links.
- Gifts are **direct charges** on the recipient's account (Checkout with the `Stripe-Account` header), since Managed Risk doesn't support destination charges. Stripe takes its fee from the charge, the donor's gross-up covers it, and the recipient keeps the whole gift. Pay My Bill takes no fee.
- Refunds and disputes come out of the recipient's Stripe balance, and Stripe covers losses it can't recover. This settles #103. Connect account and payout fees are billed to recipients under Stripe's own pricing, so most of #104 no longer falls on the platform.
- Card-gift events now come from connected accounts, so they arrive on the Connect webhook endpoint.
- Readiness means `charges_enabled` and `payouts_enabled`.

## Amendment (2026-11-09): international cards (#104)
The donor's fee covers US card pricing only. Stripe charges about 1.5% more on cards issued outside the US, and with direct charges that extra comes out of the recipient's gift (about 30 cents on $20). The owner chose to accept this and disclose it on the card form rather than overcharge every donor, block foreign cards, or build a custom payment form. Revisit if foreign cards become common.

## Amendment (2026-11-09): onboarding answers business questions (#98)
Recipients are people, not businesses, so account creation fills in what Stripe asks a business: MCC 7299 (miscellaneous personal services), statement descriptor `PAY MY BILL`, the recipient's public profile as website and support URL, and a fixed product description saying nothing is sold. Checked in test mode, this removes the industry, website, description, and descriptor questions. Onboarding still asks for the person's name, birth date, address, SSN last 4, phone, support phone, and bank.
