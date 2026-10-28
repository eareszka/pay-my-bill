# Sprint 1 — Users can sign up and post

**Dates:** 2026-11-02 → 2026-11-08 · **Goal:** a visitor can sign up, verify, set up a profile, and post a want or need that shows in the feed

Sprint Planning is Monday. #1 was pulled forward on 2026-10-27 because Sprint 0 finished early and every other story depends on it.

## Committed
| Story | Issue | Points | Status |
|---|---|---|---|
| S1-7 Data model + migrations | #1 | 3 | Done |
| S1-1 Sign up with email verification | #2 | 5 | Done |
| S1-2 Log in / log out | #3 | 2 | Done |
| S1-3 Profile with region and payment handles | #4 | 3 | Done |
| S1-4 Create a post with moderation | #5 | 5 | Done |
| S1-5 Feed of open posts | #6 | 3 | Done |
| S1-6 Post detail page | #7 | 2 | In review |

**Total:** 23 points. There's no velocity history yet, so S1-6 may carry over.

## Daily log
- 2026-10-27: Claimed #1. Added `User` and `Post` models, migration 0001, and a `flask seed` command (10 users, 20 posts). Money is integer cents (ADR 0006), and staging now runs `db upgrade` on start. Next: PR for #1, then verify staging after merge. Blocked: none.
- 2026-10-28: #1 merged. Pulled #2–#7 forward to run back to back, one PR each. Did #2: sign up, email verification, base layout, ADR 0007 (auth stack), and wireframes for the UI stories. Next: #3 log in / log out. Blocked: none.
- 2026-10-28: #2 merged (#13). The review fixes covered email-bound tokens, safe failure when mail can't send, verified TLS, and ProxyFix. The resend cooldown and async mail are filed as #14 and #15. Did #3: log in and log out, with a DB-backed lockout per account (migration 0002) and safe `next`. Next: #4 profile. Blocked: none.
- 2026-10-28: #3 merged (#16). The review hardened the lockout: insert-before-count, account+IP keying with a per-IP cap, and Retry-After. Did #4: profile form with region and handles, a handle-change email notice (T6), and a public profile page. Handles show on posts once #7 lands. Next: #5 create a post. Blocked: none.
- 2026-10-28: #4 merged (#17). The review fixed whitespace-only handles being saved and tightened the cashtag rules. Did #5: post form, $1,000 cap, 2 open posts per user, handle and rules gates, and the fundraising keyword flag that sends posts to review. After a post it redirects to `/` until #7 adds the detail page. Next: #6 feed. Blocked: none.
- 2026-10-28: #5 merged (#18). The review closed the open-post race with a row lock and the hyphen/inflection bypasses in the keyword filter. Did #6: the feed at `/` with a Want/Need filter, pagination, and progress cards. Next: #7 post detail, then a 360px browser check of every page. Blocked: none.
- 2026-10-28: #6 merged (#19). The review fixed a `?page` overflow 500 and the region display. Did #7: post detail with a visibility matrix and handles, and linked it from feed cards and new posts. 360px check: feed, rules, signup, login, public profile, post detail, new post, and profile edit were rendered in real 360px iframes (headless Edge), with no horizontal scroll. The Chrome extension wasn't connected. That check also led to dropping underlines in the top bar, because they hid the underscores in usernames. Next: sprint close-out docs. Blocked: none.

## Review
_(Sunday)_

## Retro
_(Sunday: Keep / Change / Try)_
