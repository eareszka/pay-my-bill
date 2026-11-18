# ADR 0018: Show less moves a category later in your stack

**Status:** Accepted · **Date:** 2026-11-18 · **Amends:** ADR 0013

## Context
Donors asked to see less of a kind of post they won't chip in on (#119). ADR 0013 orders the stack as the follow-through pick first, then everything else newest first. A personal preference has to fit in without hiding anyone's ask and without taking the top spot away from posters who report back.

## Decision
- Every post has one category from the owner's list (2026-11-11): Rent and housing, Bills and utilities, Groceries and food, Car and transport, Health, Kids and school, Fun and games, and Other. Posters pick it, and existing posts became Other.
- "Show less" on a ticket moves that category to the end of the viewer's stack. Within each part, posts stay newest first.
- The first ticket stays the follow-through pick (ADR 0013) whatever its category.
- Nothing is hidden. The count stays the same, and every post is still reachable.
- Logged in, the choice is saved on the account (`users.show_less`). Logged out, it's saved in a first-party, HttpOnly cookie that merges into the account at the next log in. Undo is offered right away on the feed and later on the owner's profile.

## Consequences
- Everyone's stack can differ after the first ticket, so a shared `?n=` link may open a different post for someone else.
- No new data is shared with anyone. The choice is only used to order the viewer's own feed.
- The cookie can be edited, so unknown values are dropped when it's read.
- Asking for a category is one more field on the post form.
