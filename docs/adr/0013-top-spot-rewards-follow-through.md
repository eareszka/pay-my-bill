# ADR 0013: The top of the board rewards follow-through

**Status:** Accepted · **Date:** 2026-11-03 · **Amends:** ADR 0008

## Context
The owner chose a bulletin board feed with one large ticket at the top and smaller tickets beneath it. That spot is the most visible place in the app, so what earns it shapes behavior. The owner wants it to give posters a reason to report back honestly. ADR 0008 said feed ranking isn't changed by follow-through, so this needs its own decision.

## Decision
One open post gets the big ticket, worked out from current data whenever the feed loads.

- **Out:** anyone with an overdue results update.
- **First:** posters with at least one results update posted and no net negative feedback.
- **Next:** first-time posters, so someone new with a real need can still reach the spot when no one with a record has an open post.
- **Last:** posters whose updates drew more 🤨 than kudos and 👍.
- **Within a group:** more updates plus net feedback first, then closest to its goal, then the oldest post.

The results update is the feedback. Kudos and 👍 add one point each, and 🤨 takes one away. All other posts keep their newest-first order beneath the top ticket.

## Consequences
- Following through has a visible reward, and it costs nothing to build beyond a ranking.
- ADR 0008's "feed ranking isn't changed" now applies to the rest of the board, not the top spot.
- 🤨 now affects ranking, not just what admins see, though its count stays hidden and it never removes a post.
- Feedback can be gamed (T16). Any verified account can give Kudos, so a group of accounts could lift a poster. 👍 and 🤨 need a confirmed gift. Limits belong with the admin queue.
- The feed loads all open posts to rank them. That's fine at beta size and should be revisited if the board grows large.
