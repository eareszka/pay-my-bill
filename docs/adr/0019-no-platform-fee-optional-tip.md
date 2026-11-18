# ADR 0019: No platform fee, and an optional tip on the web

**Status:** Accepted · **Date:** 2026-11-18 · **Amends:** ADR 0016 (the 1% platform fee)

## Context
App Store Guideline 3.2.1(vii) allows person-to-person gifts outside in-app purchase when the gift is optional and the full amount goes to the recipient. ADR 0016 took 1% of each card gift, which doesn't fit "the full amount" (#260). The owner still wants a way for people to support the site (#265).

## Decision
- **No platform fee.** `PLATFORM_FEE_RATE` defaults to `0`. Stripe's card fee still comes out of a card gift as in ADR 0016, and link-out gifts carry no fee at all.
- **An optional tip, web only.** Card checkout offers "Tip to support Yearnly": none (the default), $1, $2, or another amount up to $50. It's a second line item in the same Checkout session.
- **The tip never touches the gift.** The direct charge's `application_fee_amount` is the tip minus Stripe's percentage on it (`tip_kept`, with Yearnly absorbing that cost), so the recipient's share is the same as with no tip. The gift's `amount_cents`, progress, XP, and leaderboards ignore the tip. The donor's email lists it separately.
- **No tip in the iOS app.** The Capacitor shell appends `YearnlyApp` to its user agent (`appendUserAgent`). When it's there, the server leaves the tip row out and ignores any tip in the form.
- Copy says "tip" or "support Yearnly", never "donation" (Guideline 3.2.2).

## Consequences
- Yearnly earns nothing unless someone chooses to tip, and it pays about 2.9% of each tip to Stripe.
- Yearnly can't rely on the user agent for security. It only decides what to offer, and a tip sent from the app anyway is dropped on the server.
- Stripe's actual fee is rounded on the whole charge, so the recipient's share can differ from the no-tip estimate by a cent.
- The lawyer review (PB-39) confirms the tip before App Store submission.
