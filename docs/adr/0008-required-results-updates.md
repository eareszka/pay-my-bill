# ADR 0008 — Recipients must post a results update

**Status:** Accepted · **Date:** 2026-10-28

## Context
Donors give money outside the app (ADR 0002) and get nothing back except recognition. They can't tell whether the help mattered or whether the post was real. The planned thank-you post was optional, so the people most likely to skip it are the ones running "post, collect, and vanish" scams (T12).

## Decision
A results update replaces the optional thank-you post.

- **When it's owed:** a post that closes (funded, expired, or closed by the poster) with at least one confirmed donation owes one update. Partially funded posts owe one too.
- **Content:** a note of at least 20 characters, with an optional photo. Receipts or documents are never required, because needs like rent or medical bills would push people to expose sensitive information (T14).
- **Deadline:** 7 days after the post closes. Reminders go out on day 3 and day 6.
- **Penalty:** while any update is overdue, the recipient can't create new posts. Posting the late update lifts the block right away. Feed ranking isn't changed.
- **Visibility:** the update shows on the post. Every donor with a confirmed donation is notified. Kudos and 👍/🤨 reactions attach to the update.
- **Follow-through stat:** profiles show "Updated N of M funded posts." It counts only posts that owed an update.

## Consequences
- Donors see results, which closes the reward loop the app is built around.
- Scammers lose the ability to post repeatedly without accountability.
- Needs an email channel for reminders (ADR 0007's mail setup) and a daily scheduled job to mark updates overdue.
- 🤨 reactions are a signal for admins, not an automatic penalty. Repeated low-effort updates are handled by moderation (T4).
