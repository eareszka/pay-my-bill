# ADR 0016: Card gifts are flat, fees come out of the gift, and the platform takes 1%

**Status:** Accepted · **Date:** 2026-11-12 · **Supersedes in part:** ADR 0014 (donor fee gross-up, "no platform fee")

## Context
Under ADR 0014 the donor paid the gift plus Stripe's fee, so a $5 gift charged $5.46. The owner wants the donor to pay exactly the amount they type, the way most giving apps work. The owner also wants Pay My Bill to earn a small share so the site can pay for its own hosting and growth.

## Decision
- **The donor pays exactly what they enter.** Checkout's line item is the typed amount, with no gross-up.
- **Fees come out of the gift.** Stripe takes its card fee from the direct charge (estimated as 2.9% + 30¢, rounded up). Pay My Bill takes an `application_fee_amount` of **1%**, rounded up, which Stripe moves to the platform account. `PLATFORM_FEE_RATE` sets the rate, and `0` turns the fee off.
- **What counts is what the recipient gets.** The gift's `amount_cents` is the estimated net (paid − Stripe fee − platform fee), and `fee_cents` is both fees. Progress, the funded check, and the recipient's email use the net. The donor's email shows what they paid. XP stays amount-blind (ADR 0010).
- **It's disclosed before paying.** The card form says the fees come out and shows a live "<poster> gets about $X" estimate from the same rates the server uses. The Terms spell out the fees and say link-out gifts carry no Pay My Bill fee.
- The $5 minimum stays. At $5, fees are about 10% of the gift (45¢ + 5¢).

## Consequences
- A $5 gift → the recipient gets about $4.50. A $20 gift → about $18.92. A $100 gift → about $95.80.
- The net is an estimate. Stripe charges about 1.5% more on cards from outside the US, so those recipients get a little less than counted (the shortfall accepted in ADR 0014 now also applies to the counted amount).
- Pay My Bill now earns revenue from gifts. Application fees are taxable income, and the Stripe platform profile and the App Store review (PB-9, Guideline 3.2.1(vii)) must describe the fee. Revisit the rate before the App Store submission.
- Refunds happen in Stripe, not in the app. Stripe doesn't return the application fee on a refund unless it's asked to (`refund_application_fee`), so without that the recipient's balance covers the platform's 1%. Whoever refunds should also refund the application fee.
