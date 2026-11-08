# ADR 0004 — Only recipient-confirmed donations count

**Status:** Accepted · **Date:** 2026-10-27

## Context
Payments happen outside the app (ADR 0002), so a donor's "I sent $X" can't be trusted on its own. Leaderboards and rewards would be trivial to game.

## Decision
A donation starts as `pending`. Only after the recipient marks it `confirmed` does it count toward XP, badges, streaks, leaderboards, and post progress. A `disputed` donation earns nothing.

## Consequences
- Rewards are only as honest as recipients are. Collusion is handled separately: per donor→recipient weekly cap, account-age gate, verified email, and admin flags (see `docs/threat-model.md`).
- Donor rewards are delayed until the recipient confirms, so the confirm prompt has to be quick and noticeable.

## Amendment (2026-11-08, ADR 0014)
Card gifts paid through Stripe Checkout are recorded as confirmed when Stripe's signed webhook reports them paid, because the processor verified the payment and the recipient doesn't need to. A refund or card dispute reported by Stripe un-counts the gift by marking it disputed.
