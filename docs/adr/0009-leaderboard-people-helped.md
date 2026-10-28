# ADR 0009 — Leaderboards rank donors by people helped

**Status:** Accepted · **Date:** 2026-10-28

## Context
The PRD planned leaderboards without saying what they rank. Ranking by dollars given favors wealthy donors over generous ones. It also rewards round-tripping (T11): two accounts send the same money back and forth, both confirm, and the dollar total grows with no real cost. The $200/week per-pair cap only limits how fast that works.

## Decision
Global, state, and city leaderboards rank donors by the number of **distinct recipients** they helped in the period. A recipient counts once they confirm at least one donation from that donor (ADR 0004). Ties break by the earliest time the count was reached. Dollar totals can be shown on a donor's profile but are never used for ranking.

The existing eligibility rules still apply: verified email, account older than 3 days, and the per-pair weekly cap flag.

## Consequences
- Round-tripping between a fixed set of accounts can't raise rank. Gaming the board requires many distinct recipient accounts, and that ring pattern is easier to flag.
- A $5 gift and a $500 gift count the same, which fits the goal of a community where anyone can help.
- XP and badges can still use amounts. This ADR only covers leaderboard ranking.
