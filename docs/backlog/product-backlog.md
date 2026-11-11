# Product Backlog

Stories and spikes that aren't in a sprint yet. Pull them in at Sprint Planning. UI stories still need a wireframe to meet the Definition of Ready. `docs/roadmap.md` gives the order.

---

### PB-7 Terms of Service and Privacy Policy pages · #32 · 2 pts · P0 · epic:safety
- [ ] `/terms` and `/privacy` exist and are linked in the footer and on the signup form.
- [ ] Terms state: 18+, no business fundraising, the app never holds money, needs aren't verified, and donations are gifts at the donor's own risk.
- [ ] Marked as drafts; a lawyer review is a v1.0 gate (PRD).

### PB-8 Staging Postgres before it expires · #33 · 1 pt · P0 · chore
- [ ] Before 2026-11-26, staging Postgres is either on a paid plan or recreated, with the steps written in the README.

### PB-9 Spike: payment-app terms · #34 · 2 pts · P1 · spike
- [ ] A short write-up in `docs/research/` on what Cash App, Venmo, and PayPal allow for soliciting personal payments, deep-link rules, and 1099-K implications for recipients.
- [ ] Whether cosmetic perks (PB-30) fit Apple's Guideline 3.2.1(vii), that gifts stay optional and go entirely to the recipient.
- [ ] Any required changes become backlog items or a new ADR.

### PB-10 Spike: product name and domain · #35 · 2 pts · P2 · spike
- [ ] Three or more candidate names, each checked against USPTO search, domain availability, and app-store conflicts.
- [ ] The owner picks one; an ADR records it.

### PB-11 Spike: cold start and beta recruitment · #36 · 2 pts · P2 · spike
- [ ] A plan for getting the first 20–50 beta users, including where donors come from, and how the PRD success metrics will be measured.

---

## Toward the App Store (see `docs/roadmap.md`)

### PB-12 Block another user · #TBD · 3 pts · P1 · epic:safety · v0.1-alpha
As a **user**, I want to **block someone** so that **I stop seeing them and they can't interact with me** (App Store Guideline 1.2).
- [ ] Given another user's profile or post, when I block them, then their posts and updates are hidden from my feed.
- [ ] Given they've blocked me or I've blocked them, then neither of us can pledge to the other's posts or give kudos.
- [ ] Given my blocked list in settings, when I unblock someone, then their content shows again.
- [ ] Blocking is silent: the blocked user isn't notified.

### PB-13 Production hosting, domain, and HTTPS · #TBD · 3 pts · P0 · chore · v0.2-beta
- [ ] ADR 0011 records the production host, plan, and monthly cost.
- [ ] Production auto-deploys from tagged releases, separate from staging, on the domain chosen in PB-10, with HTTPS.
- [ ] `SESSION_COOKIE_SECURE` and the other production settings come from env vars and are listed in `.env.example`.

### PB-14 Transactional email provider · #TBD · 2 pts · P0 · epic:accounts · v0.2-beta
- [ ] `MAIL_SERVER` points at a provider (Postmark, Resend, or SES) with SPF and DKIM set up on the domain.
- [ ] A verification email from production lands in the Gmail and iCloud inboxes, not spam.

### PB-15 Monitoring and backups · #TBD · 2 pts · P1 · chore · v0.2-beta
- [ ] Unhandled errors are reported to an error tracker, with no passwords or tokens in the payload.
- [ ] An uptime check on `/health` alerts the owner.
- [ ] Daily Postgres backups, and a restore that's been tested once and written down in the README.

### PB-16 Spike: Capacitor iOS wrapper · #TBD · 3 pts · P1 · spike · v1.0
- [ ] A Capacitor project that loads the production site, with a write-up in `docs/research/`.
- [ ] A plan for the native features that clear Guideline 4.2: push notifications, the share sheet, and an offline screen.
- [ ] ADR 0012 records the decision.

### PB-17 Spike: iOS builds on macOS CI · #TBD · 2 pts · P1 · spike · v1.0
- [ ] A GitHub Actions macOS workflow builds and signs the app and uploads it to TestFlight, with the signing secrets in GitHub secrets.

### PB-18 Apple Developer enrollment · #TBD · 1 pt · P1 · chore · v1.0 · owner
- [ ] Decide on an individual or organization (LLC) account after the Phase 5 legal review. Get a D-U-N-S number if it's an organization.
- [ ] Enrolled ($99/year), with the account holder recorded in the README.

### PB-19 App Store listing and review pack · #TBD · 3 pts · P1 · chore · v1.0
- [ ] App Store Connect listing: name, description, icon, 6.7" and 6.5" screenshots, a privacy policy URL, and a support URL.
- [ ] A privacy label covering email, payment handles, and user content. An age rating that matches the 18+ rule.
- [ ] A demo account and review notes covering link-out gifts (Guideline 3.2.1(vii)), reporting, blocking, and account deletion.
- [ ] User-facing copy says "gift" or "chip in", never "charitable donation".

### PB-20 Photo on a results update · #69 · 2 pts · P3 · epic:posts
Moved out of PB-1 by the owner (2026-11-02). Text-only updates ship first.
- [ ] Given an optional photo, when I upload it, then the type and size are validated and it's stored under a random filename (T7).

### PB-22 The 30 days start when a flagged post is approved · #68 · 1 pt · P1 · epic:safety
From the PR #66 review. Do this with the admin queue, which adds approval. Today the clock runs from `created_at`, so time in review uses up a post's open window.
- [ ] Given a flagged post approved on day 25, then it stays open for 30 days from approval.

### PB-23 Show reaction counts in the admin queue · #73 · 1 pt · P2 · epic:safety
From the PR #72 review. Deleting a post hides its update and reactions, so admins lose the 🤨 signal (ADR 0008). The rows stay in the database.
- [ ] Given a post with 🤨 reactions, deleted or not, when an admin opens the queue, then they see the count.

### PB-24 Keep the stack steady while browsing · #87 · 2 pts · P2 · epic:posts
From the PR #86 review. Next ticket uses a position, so a new or closed post can repeat or skip a ticket mid-browse. A stable cursor would fix it. Done as part of PB-27.
- [ ] Given a post is added or closes while I'm browsing, when I tap Next ticket, then I don't see a repeat or miss a post.

### PB-25 Rotate older posts forward · #88 · 2 pts · P2 · epic:posts
From the owner's choice of One Ticket at a Time. Posts deep in the stack may rarely be seen. Revisit in the closed beta, since posts close at 30 days and PB-27 spaces new posts in.
- [ ] Given a post far back in the stack, it gets a fair turn near the front.

### PB-26 Owner's open design decisions from the board review · #89 · 2 pts · P2 · epic:posts
From the PR #86 finish review. Each one is the owner's call, since it changes the approved look or flow.
- [ ] Reaction emoji: keep 👍 and 🤨, or replace them.
- [ ] Green links and progress marks: keep them, or reserve green for main buttons.
- [ ] Rules and profile text on cork: move it onto white tickets, or leave it.
- [ ] "I sent it" on the feed: stay at the same ticket, or go to the post page.
- [ ] Need or Want on phones: add a small label, since only color shows it today.

---

## Match the concept (owner, 2026-11-04)

### PB-27 Rank the whole stack · #TBD · 5 pts · P1 · epic:posts · v0.1-alpha
As a **donor**, I want **the stack to lead with people who follow through and posts near their goal** so that **my gift goes somewhere it counts**. Only the first ticket is ranked today. Amends ADR 0013. Includes PB-24.
- [ ] Each ticket's score combines the poster's record (updates plus capped kudos), thanks (capped low), and closeness to goal, counting only gifts and reactions from established accounts.
- [ ] Every 4th ticket is the newest post not yet shown.
- [ ] Overdue posters and posters with no way to be paid come last.
- [ ] Given a post is added or closes while I'm browsing, when I move on, then I don't see a repeat or miss a post. Moving is by post, not by position.
- [ ] The All, Needs, and Wants filters each keep this order.

### PB-28 Remove local area · #TBD · 3 pts · P1 · epic:leaderboards · v0.1-alpha
The owner sees no reason for it now. Updates ADR 0009, `AGENTS.md`, `PRODUCT.md`, `DESIGN.md`, and the threat model.
- [ ] City and state are gone from signup, profiles, posts, and the database (the migration runs up and down).
- [ ] Leaders is one list, still ranked by people helped.
- [ ] The Local hero badge is gone.
- [ ] A search finds no leftover references, apart from history in the changelog, old sprint records, and ADRs.

### PB-29 Show donor rewards at the right moment · #TBD · 3 pts · P1 · epic:rewards · v0.1-alpha
As a **donor**, I want to **see what my gift earned when it happens** so that **giving feels rewarding**. Builds on S5-4 (#80). Only confirmed gifts count (ADR 0004).
- [ ] After "I sent it", the donor sees what happens next.
- [ ] Once the recipient confirms, the donor sees the XP, streak, and any new badge.
- [ ] The donor's level shows beside their username.
- [ ] A donor is told when someone they helped posts an update.
- [ ] `rules.html` no longer says donors get nothing back but thanks.

### PB-30 Perks that unlock · #TBD · 3 pts · P2 · epic:rewards · v0.1-alpha
As a **donor**, I want **levels to unlock something** so that **I have a reason to keep giving**. The owner picks the perks before this starts.
- [ ] Perks are cosmetic only, such as a profile frame or a highlighted name.
- [ ] A perk never changes where your own posts sit in the stack.
- [ ] Unlocks come only from confirmed gifts, and PB-9 has checked them against Apple's rules.

### PB-31 One-tap thank you on a confirmed gift · #125 · 3 pts · P1 · epic:donations · v0.1-alpha
As a **recipient**, I want to **thank a donor directly** so that **they know it mattered**, and it helps my place in the stack.
- [ ] On a confirmed gift, the recipient can send one thank you, with an optional short note.
- [ ] Only that donor sees it, by email and on a Gifts banner.
- [ ] Thanks count toward the recipient's score with a low cap, and only for established donors, so a second account can't farm it.
- [ ] (Owner, 2026-11-09) If the donor left a note with their gift (PB-45), the thank-you can answer it. One exchange per gift, no thread. Follows the message guardrails below.
- [ ] The thank-you box opens inside the gift on the Gifts page once the poster confirms it. If the note is shared, the reply shows under it in "How it's going".

### PB-32 Simple navigation and clear tickets · #TBD · 3 pts · P1 · epic:posts · v0.1-alpha
As **anyone**, I want to **find my way around and see what a person is asking for at a glance**. Goes through Impeccable, shown to the owner first. Settles PB-26.
- [ ] The top bar reads feed, Post, Gifts, Leaders, profile, and Log out moves to the profile.
- [ ] Rules, Terms, and Privacy are in a footer.
- [ ] A gift that didn't arrive uses one word everywhere.
- [ ] A ticket shows its title, "$X raised of $Y", and a Need or Want label on phones. The owner chooses whether to add a small progress bar.

---

## Safe to open and production

### PB-33 Report a post or user, with an admin queue · #TBD · 5 pts · P0 · epic:safety · v0.1-alpha
As the **community**, we want **a way to report and act on bad posts** (App Store Guideline 1.2). Keyword-flagged posts have no way to be approved today. Do PB-22 and PB-23 with this.
- [ ] Any verified user can report a post or user, with a reason.
- [ ] Admins see reports and flagged posts in one queue, and can approve, remove, or ban.
- [ ] A banned user can't log in, and their open posts leave the feed.

### PB-34 Production settings and security headers · #TBD · 2 pts · P0 · chore · v0.2-beta
- [ ] Secure session cookies, security headers, and an upload limit are on in production.
- [ ] The app refuses to start in production without `SECRET_KEY`.

### PB-35 Scheduled jobs for reminders · #TBD · 1 pt · P1 · chore · v0.2-beta
- [ ] `flask gifts remind` and `flask posts remind` run daily without anyone starting them.

### PB-36 Installable web app · #TBD · 3 pts · P1 · v0.2-beta
- [ ] A manifest and icons let people add the site to a phone's home screen, and an offline screen shows when there's no connection. Pages with money or personal data aren't cached.

### PB-37 Browser tests in the repo · #TBD · 2 pts · P2 · chore · v0.2-beta
- [ ] `tests/e2e` covers swiping and the chip-in flow.
- [ ] Swiping has been checked by hand in Safari on an iPhone.

### PB-38 Run the closed beta · #TBD · 3 pts · P1 · chore · v0.2-beta
Follows PB-11's recruitment plan.
- [ ] 10 to 30 invited people use the production site, and their feedback becomes issues.
- [ ] PB-25 and PB-40 are decided from what they show.

### PB-39 Lawyer review of Terms and Privacy · #TBD · 1 pt · P0 · chore · v1.0 · owner
- [ ] A lawyer has reviewed both pages, and the owner has decided on an LLC, which decides the Apple account type in PB-18.

### PB-40 Photos on posts · #TBD · 5 pts · P3 · epic:posts
Comes after PB-33, since photos need moderation. Compare cloud storage options and bring the cost to the owner first, with an ADR (T7).
- [ ] Given an optional photo, when I upload it, then the type and size are validated and it's stored under a random filename.

---

## Instant gifts (owner, 2026-11-08)

### PB-41 Spike: Stripe Connect approval · #TBD · 2 pts · P0 · spike · owner
ADR 0014. The owner applies. Nothing about real payments ships until this is done.
- [ ] Stripe account with Connect (Express) enabled, and the platform profile describes personal gifting with no business or charity fundraising.
- [ ] Stripe's answer on the crowdfunding review is recorded in `docs/research/`, along with fees and dispute liability.
- [ ] PB-9 is updated for Apple Guideline 3.2.1(vii) with Stripe fees.

### PB-42 Recipients connect Stripe · #TBD · 3 pts · P0 · epic:donations
- [ ] From their profile, a recipient starts Stripe-hosted Express onboarding and comes back to a clear status: not started, pending, or ready.
- [ ] Only ready recipients can take card gifts. Account status is updated from the `account.updated` webhook.

### PB-43 Instant card gifts · #TBD · 5 pts · P0 · epic:donations
- [ ] A donor picks an amount and pays with card, Apple Pay, or Google Pay through Stripe Checkout, as a destination charge to the recipient with no platform fee.
- [ ] A signed, idempotent webhook records the gift as confirmed at once (amending ADR 0004), and the donor sees their rewards.
- [ ] Refunds and disputes from Stripe un-count the gift and flag it in the admin queue.
- [ ] Terms and Privacy are updated for card gifts.

### PB-44 Share an ask · #TBD · 2 pts · P2 · epic:posts
From the #118 finish review: the full-screen feed's rail has room for Share.
- [ ] A Share button on the rail and post page opens the phone's share sheet, or copies the post link where that isn't available.

### PB-48 Photos on our own domain · #TBD · 1 pt · P1 · epic:launch
Staging serves photos from R2's public development URL, which Cloudflare rate-limits and doesn't intend for production (ADR 0015).
- [ ] Before launch, connect a custom domain to the production bucket, turn off its development URL, and set `R2_PUBLIC_URL` to the custom domain.

## Donors and posters talking (owner, 2026-11-09)
The owner wants donors and posters to be able to talk and posters to keep donors in the loop, without open comments. Every message is short, tied to a real gift or post, and private unless stated otherwise. There are no threads: at most one reply. Order: after #119 and #120. PB-31 (thank-you with a reply, #125) belongs to this group.

**Shared design** (the owner approved the mockup on 2026-11-09: https://claude.ai/artifact/5MUbEMb4eFFSVL7k9tS86n, built in Impeccable in the current look):
- [ ] Each post has one list, "How it's going", newest first. It holds the poster's updates, gift notes their donors chose to share, and answered questions. Every item has the same shape: who, what kind ("update", "chipped in", "asked"), when, the text, and at most one indented reply from the poster.
- [ ] On the post page, Chip in comes first and stays the one main action. Follow is a single quiet button. The list follows the story.
- [ ] The feed card adds only one line when there's news ("Updated 2 hours ago"), never a preview box.
- [ ] On a computer, the list is in the left column, and Chip in and Follow stay on the right.

**Message guardrails** (apply to every story here):
- [ ] Notes, replies, updates, and answers are plain text with a character limit. Phone numbers, links, emails, and payment handles are masked, so nobody gets pulled off the app (T3, T4).
- [ ] Every message can be reported into the existing `/admin` queue, and admins can remove one message on its own. Blocking (PB-12) hides a blocked person's messages both ways.
- [ ] Rate limits on writing, and emails batched to at most one a day per person per post.
- [ ] Deleting a post or account removes its messages, the same as photos.

### PB-45 Note with your gift · #124 · 3 pts · P1 · epic:donations
As a **donor**, I want to **send a few kind words with my gift** so that **the person knows someone is rooting for them**.
- [ ] When recording "I sent it" (or a card gift), the donor can add an optional note of up to 200 characters, behind an "Add a note to your gift" link, so the box is hidden until they want it.
- [ ] The poster sees the note inside the gift on their Gifts page while confirming it.
- [ ] The donor chooses whether the note also shows in the post's "How it's going" list, under the donor's username. It is private by default.
- [ ] Only someone who recorded a gift can leave a note, so there's nothing for spammers to post into.

### PB-46 Progress updates and following a post · #126 · 5 pts · P1 · epic:posts
As a **poster**, I want to **tell donors how it's going while my post is open**, and as a **visitor** I want to **follow a post** so that **I see how it turns out**.
- [ ] The poster can post a short update (up to 500 characters, with an optional photo through #122) while the post is open, at most 3 a day. The box sits at the top of "How it's going" on their own post.
- [ ] Updates show in "How it's going". When the post closes, the results update (ADR 0008) is the newest entry.
- [ ] Donors and followers get an email for new updates, at most one a day per post. They can stop following from the email or the post.
- [ ] Anyone logged in can follow a post without giving.
- [ ] Updates take kudos (a heart with a count, no 👍/🤨, and no replies), and only results updates count toward the top spot (ADR 0013).
- [ ] The feed card shows "Updated <time> ago" for 3 days after an update.

### PB-47 Questions before giving · #127 · 3 pts · P2 · epic:posts
As a **visitor**, I want to **ask the poster a question before I give** so that **I can trust what I'm chipping in for**. Pairs with Trust information (#79).
- [ ] A verified user can ask a question of up to 200 characters on an open post, from an "Ask <poster> a question" link at the end of "How it's going". It is private until answered.
- [ ] The poster can answer it, which adds the question and answer together to "How it's going", or dismiss it. One answer per question, no thread.
- [ ] A question that's never answered is never shown publicly.
- [ ] At most 3 open questions per asker per post.

### PB-49 Catch farms that use a helper account · #146 · 3 pts · P2 · security
From the audit's re-test of #140. A farmer plus one extra account that both give 1 cent to the same puppets avoids the flag, and both get credit.
- [ ] Flag a group of recipients that share the same small set of givers when every confirmed gift in the group is tiny.
