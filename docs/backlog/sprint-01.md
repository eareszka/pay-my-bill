# Sprint 1 Backlog — "Users can sign up and post"

All stories meet the Definition of Ready, except the wireframes, which are attached during refinement.

---

### S1-1 Sign up with email verification · 5 pts · P0 · epic:accounts
As a **new user**, I want to **create an account and verify my email** so that **I can post and donate**.
- [ ] Given valid username/email/password, when I submit, then an account is created with a hashed password and a verification email (logged to the console in dev) is sent.
- [ ] Given a duplicate username or email, when I submit, then I see an error and no account is created.
- [ ] Given an unverified account, when I try to post or donate, then I'm prompted to verify first.
- [ ] All forms carry CSRF tokens (T8).

### S1-2 Log in / log out · 2 pts · P0 · epic:accounts
As a **user**, I want to **log in and out** so that **my account stays mine**.
- [ ] Given correct credentials, when I log in, then I land on the feed with a session.
- [ ] Given 5 failed attempts in 15 minutes, when I try again, then I'm rate-limited (T6).
- [ ] Given I'm logged in, when I log out, then my session ends.

### S1-3 Profile with region and payment handles · 3 pts · P1 · epic:accounts
As a **poster**, I want to **set my city/state and my Cash App/Venmo/PayPal handles** so that **people can pay me and regional boards work**.
- [ ] Given the profile form, when I save valid handles, then they're stored and shown on my posts.
- [ ] Given I change a handle, when I save, then an email notice is sent (T6).
- [ ] The region is free-text city and state; no GPS (T10).

### S1-4 Create a post with moderation · 5 pts · P0 · epic:posts
As a **poster**, I want to **post a want or need with a goal amount** so that **others can help**.
- [ ] Given a goal above $1,000, when I submit, then it's rejected with a message.
- [ ] Given I already have 2 open posts, when I submit a third, then it's rejected.
- [ ] Given text that matches the fundraising keyword list, when I submit, then the post goes to `pending_review` and isn't shown in the feed.
- [ ] Given I have no payment handle, when I try to post, then I'm sent to my profile first.
- [ ] Before my first post, I must agree to the Community Rules.

### S1-5 Feed of open posts · 3 pts · P1 · epic:posts
As a **visitor**, I want to **scroll open posts** so that **I can find someone to help**.
- [ ] Given open posts, when I open `/`, then I see cards (title, category chip, goal, progress) with the newest first.
- [ ] I can filter by Want or Need.
- [ ] The layout has no horizontal scroll at 360px width.

### S1-6 Post detail page · 2 pts · P1 · epic:posts
As a **visitor**, I want to **open a post** so that **I can read the full story and see how to help**.
- [ ] Given a published post, when I open it, then I see the body, the poster, the goal, and the progress.
- [ ] Given a removed or pending-review post, when someone other than the owner or an admin opens it, then they get a 404.

### S1-7 Data model + migrations · 3 pts · P0 · type:chore
- [ ] User and Post models with Alembic migration 0001.
- [ ] `seed.py` creates 10 users and 20 posts for dev.

**Total: 23 pts.** This is a first-sprint guess with no velocity history yet. Expect to carry over S1-6 if needed.
