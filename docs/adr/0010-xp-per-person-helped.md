# ADR 0010: XP per person helped

**Status:** Accepted · **Date:** 2026-10-31

## Context
Donors are the primary user, and rewards should make giving feel like progress. ADR 0009 ranks leaderboards by people helped but left XP open to amounts.

## Decision
The owner chose amount-blind XP: each confirmed gift earns 10 XP, and the first confirmed gift to a new person earns 25 more. Level L starts at 50 × L × (L − 1) XP. Rewards are computed from gifts when read, in `app/rewards.py`, with no stored counters. A gift counts only if it's confirmed (ADR 0004), isn't on a removed post, and went to a verified recipient whose account is at least 3 days old (T2).

## Consequences
- A $5 gift earns as much as a $500 one, which keeps the focus on helping more people, not spending more.
- Sock-puppet farming needs aged, verified accounts that confirm gifts, which makes it slower and more visible.
- Computing on read is fine at beta scale. If profiles get slow, cache the totals.
