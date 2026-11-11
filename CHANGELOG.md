# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Changed
- When a post offers "Chip in instantly" by card, the Cash App, Venmo, and PayPal buttons below it are outlined, so the card stays the one filled button. With no card option they stay filled (owner, 2026-11-11).

### Added
- A how-it-works home page for new visitors (#120). Logged out, `/` opens on two color fields, "I want to help" and "I need a hand". Each path walks through its steps as full-screen fields that cut in sideways as you scroll, the way the feed moves, with the real app pieces beside them labeled Example. It ends at the sign-up form. The feed moves to `/feed`; logged-in users and old feed links go straight there. With reduced motion, or in browsers without scroll-driven animation, it's a plain stacked page.
- Your posts and what you chipped in on, in one place (#132). "You" in the nav opens your own profile, with Posts and Chipped in tabs and a Settings button. Posts starts with any gifts waiting for you to confirm, then each post with what comes next: open until a date, update due, or update overdue. The Gifts tab folds into You (its count badge moves there), and old Gifts links still work. Visitors see your posts but not what you gave. The confirm list no longer shows stray bullets.
- Profiles list the person's posts with their state and amount raised. Posters can edit or delete their own posts from there. Before the first gift, every field can be edited; after it, only the story. Edited posts show "Edited <date>", and an edit that hits the fundraising word list goes back to review (#116).
- A photo on a post (#122, ADR 0015). Posters can add one optional JPG, PNG, or WebP photo, up to 8 MB. It fills the card on the feed and the header on the post page. Every photo is turned upright, shrunk to 1600px, and rebuilt as a WebP with its hidden details removed, including where it was taken. Photos are stored in Cloudflare R2 when `R2_*` is set, or in a local folder otherwise. Posters can remove their photo, people can report an "Inappropriate photo", and admins can remove just the photo from the queue. Deleting a post or account deletes its photos. The Privacy page says so. The local seed gives five posts CC0 placeholder photos.

### Changed
- The app no longer says "donor". Pages and emails say "people who chipped in", "the person who sent it", or "whoever sent them" instead: the leaderboard hint, the delete-post and delete-account prompts, the Community Rules, and the pending-gift reminder email.
- New look: the card stack (#118). The owner replaced the cork board through Impeccable with a full-screen feed: each person's ask fills the screen in its own color (red for a need, blue for a want, until categories arrive in #119), with a tall League Gothic title, who and where, the story, and the amount on the card. Back and Next sit on a rail at the right edge, and the one you drag toward lights up as the real next ask shows underneath. Swipes snap in 180ms. Chip in is a white button on every ask. The shell is void black with a bottom nav on phones (Feed, Post, Gifts, Leaders, you) that moves into the top bar on wide screens. The feed and post pages are always dark, and forms, Gifts, Leaders, and profiles follow the system light or dark setting in the same type. On screens 960px and wider, the feed card takes the post page's shape: the ask and the Chip in panel form one wide card, with big Back and Next buttons outside it and arrow keys, so nobody has to drag with a mouse. League Gothic replaces Bitter (both OFL).

### Security
- When a password reset confirms an email for the first time, the account's payment handles and city are cleared and the owner is told, so a handle saved by whoever signed up with that email first can't collect the owner's gifts (#133).
- Resetting a password now logs out every session on that account, so someone who signed up with another person's email and stayed logged in loses access once the real owner claims it through a reset link. Logging in or signing up also starts a fresh session (#130, migration 0016). Everyone gets logged out once when this deploys.
- Password reset links no longer carry the account's password hash. Signed links can be read by anyone who sees them, so a forwarded or logged reset email could have been cracked offline. Links now hold a keyed digest instead, and still work only once (#134). Reset links sent before this deploys stop working; ask for a new one.
- Sign-up is limited to 10 new accounts an hour from one internet address, so nobody can make a farm of accounts or use up the daily email quota with verification emails to strangers. A household or campus network sharing an address still has room (#137).
- A ban now hides the user everywhere: all their posts (closed and funded ones too) and photos are removed, so gifts to them stop counting; they drop off every leaderboard and stop counting toward who gets the top of the feed; their profile is 404 to everyone but admins; and they can no longer be reported (#147).
- When an admin removes a post, or bans a user and so removes their open posts, the photos are deleted too. Before, the post was gone but its photo link still worked (#144).
- The admin queue flags possible fake helping: a donor where 3 or more of the people they helped got nothing from anyone outside that group (banned accounts don't count as outside) and joined within a day of each other. Each flag shows what the donor gave each account, and admins can ban the donor alone or the donor and the flagged accounts together. Flags never change the leaderboard, and gifts of any size still count (#140).
- The session cookie is now Secure on HTTPS (decided from `APP_URL`) and SameSite=Lax everywhere. Every page sends a strict Content Security Policy (scripts, styles, and fonts from the site only, photos from the site or R2, forms only to the site or Stripe), refuses to be framed, and sends nosniff and a same-origin referrer policy. HTTPS deployments also send HSTS for a year (#142).
- When an admin removes a post, or bans a user and so removes their open posts, the photos are deleted too. Before, the post was gone but its photo link still worked (#144).
- Links in emails and the return links sent to Stripe are now built from `APP_URL`, not the address the request came in on, so a forged Host header can't send someone a reset or verify link pointing at another site (#150).
- The app refuses to start unless `SECRET_KEY` is a random value of at least 32 characters and `APP_URL` is https. Only clear development (`FLASK_ENV=development`, debug mode, or tests) can skip this, so a deploy that forgets a variable fails loudly instead of running insecurely. Before, a deploy missing the key would have made sessions and email links forgeable, and one missing `APP_URL` would have sent http://localhost links with an insecure cookie (#152).
- One slow request no longer stalls the whole site: staging runs gunicorn with 4 threads (one process, to fit the free plan's memory) and a 60-second timeout. Photos decode one at a time, and JPEGs decode at reduced size. Request bodies are capped at 1 MB except on the new-post form, which keeps 9 MB for a photo (#155).
- The fundraising word check now sees through disguises: look-alike letters from other alphabets, accents, hidden characters, digits for letters ("bus1ness"), and spaced-out letters ("b.u.s.i.n.e.s.s"). Posts are also checked for company, funding, capital, profit, return on, angel, shop, and "my brand" (not "my brand new"), with Los Angeles, Capital One, "stock up", and non-profit left alone; a match still only sends the post to review. Results updates, which are refused rather than reviewed, keep the original shorter list, and the message now names the word (#158).
- A verification link now confirms an email only in a browser logged in to that account. Opened while logged out, it asks you to log in, or to reset the password if you never made the account, which takes it over and clears anything a squatter set. Opened from another account, it does nothing. The email now says what to do if you didn't sign up (#160).
- A banned account's login gets the same "Wrong username, email, or password" reply as a wrong password, so the reply no longer confirms that a guessed password was right (#163).
- With no mail provider set, emails are written in full to the log only in development, debug, or tests. Anywhere else the log shows just the recipient and subject, with a warning, so reset and verify links never end up in shared logs (#165).
- The Stripe refresh link, where Stripe sends people when an onboarding link expires, only renews onboarding already started. It no longer creates a Stripe account, so a link from another site can't make one for a logged-in user (#167).
- Deleting an account now also clears its password-reset and verification-email throttle rows, so a deleted user's email address doesn't stay in the database (#169).
- Logging out now clears the whole session, so nothing from the visit (a saved way back, the form token) carries over to whoever uses the browser next (#171).
- Admins can be removed with `flask --app app admin revoke <email>`. Every admin action (approve, remove a post or photo, ban, dismiss, grant, revoke) is recorded with who did it and when, and /admin lists the 25 most recent. Admin pages return 404 for ids too large for the database instead of an error (#173, migration 0017).
- Verification emails are limited to three an hour per account (signup plus two resends), so one account can't use up the daily email quota (#14).

### Changed
- Emails sent during a page or webhook (verification, reset, gift and update notices, handle changes, admin alerts) now go out on a background thread, so a slow mail service no longer holds up sign-up or Stripe's webhook. Failures are still logged. Sign-up and resend now always say the link is on its way (#105).

### Changed
- Stripe onboarding skips the business questions. Pay My Bill fills in the industry, website (the recipient's profile), product description, and statement descriptor, so recipients only give their personal and bank details (#98).

### Changed
- The verify page and the password reset message tell people to check their spam or junk folder, and to mark the email "Not spam" on the verify page. Without a domain of our own, Pay My Bill's emails often land there.

### Changed
- The database moved from Render's free Postgres, which expires, to Neon's free tier (ADR 0005 amendment, #33).

### Changed
- The card form says that a card from outside the US costs a little more, and that it comes out of the gift (#104).

### Fixed
- Card checkout offers only cards, Apple Pay, and Google Pay. Other methods have different fees that the donor's fee doesn't cover (#108).

### Changed
- Card gifts now use Stripe Managed Risk (ADR 0014 amendment). Recipient accounts are created with Accounts v2 with Stripe covering losses, and gifts are direct charges on the recipient's account. Refunds and disputes come out of the recipient's Stripe balance, not the platform's. The test setup also blanks Stripe and mail keys, so a developer's `.env` can't reach real services from tests.

### Added
- Swipe through the pile (#90). On the feed, swipe left for the next ticket and right to go back, with the ticket moving like mail being dealt off a pile and the real neighboring post already underneath. Back, Next ticket, and the arrow keys play the same motion. Swiping never gives or hides a post, and the links still work without JavaScript.
- Instant card gifts (PB-43, ADR 0014). When the recipient has connected Stripe, the Chip in panel leads with Chip in instantly: card, Apple Pay, or Google Pay through Stripe Checkout, from $5 up to the goal. The donor covers the card fee, so the recipient gets the whole gift as a destination charge. A signed webhook records the gift as confirmed at once, with no recipient step (amending ADR 0004), and emails both sides. Retried deliveries are ignored. Refunds and card disputes un-count the gift and email admins. `account.updated` keeps each recipient's readiness current. App links stay as the fallback. The Terms add the Stripe Connected Account Agreement, and the Privacy Policy names Stripe (migration 0012).
- Recipients can connect Stripe (PB-42, ADR 0014). With `STRIPE_SECRET_KEY` set, the profile has a Card and Apple Pay gifts section that starts Stripe-hosted Express onboarding. Coming back records whether the account can take transfers and pay out, and connected recipients get a link to their Stripe payouts page. A recipient with only Stripe connected can now post (migration 0011).

### Added
- One-tap confirm. The "sent you a gift" email now links to a page that asks "Did $20 arrive?" with Yes and No buttons, and it works without logging in. The link is signed, tied to that recipient, and expires with the gift after 14 days. Opening it only shows the question, so email scanners can't answer it. Confirming from email does everything confirming on the Gifts page does.

### Fixed
- Venmo pay buttons now open `account.venmo.com/pay`, Venmo's current web pay page. The old `venmo.com/?txn=pay` link was blocked with a 406.

### Added
- Email through Brevo's HTTPS API when `BREVO_API_KEY` is set, because Render's free tier blocks outbound SMTP. SMTP and the console backend still work as before.
- Reports and an admin queue (PB-33, #68). Verified users can report a post or a person, with a reason and an optional note. Each person can have one open report per target, and admins get an email for every report and every flagged post. `/admin` shows flagged posts and open reports in one queue. Admins can approve a flagged post, whose 30 days then start at approval, remove a post, ban a user, or dismiss a report. A banned user's open posts are removed, their sessions end, and they can't log in. `flask --app app admin grant <email>` makes an admin (migration 0010).
- Password reset (#82). Log in links to "Forgot your password?", which always gives the same reply, so it can't reveal who has an account. The emailed link expires in an hour and stops working once the password changes. Requests share the login rate limit. A reset clears a lockout, verifies the email, and emails a notice that the password changed.
- Terms of Service and Privacy Policy pages (#32), as drafts pending legal review. They're linked in a new footer beside the Rules, and signup now asks people to confirm they're 18 or older and agree to both. `CONTACT_EMAIL` sets the address shown on the pages, and `render.yaml` lists the mail settings for Gmail SMTP.

### Documentation
- The roadmap and backlog now set out the owner's path to launch: match the concept, make it safe to open, go to production, run a closed beta, then the App Store.

### Changed
- Bulletin board redesign (#85). The owner replaced the rack: every page now uses a cork ground, a wood top bar, and plain square tickets, with leaf green for primary actions, links, and progress marks. The feed shows one large ticket at a time with a tear-off Chip in tab and Next ticket, replacing the scrolling list. On screens 960px and wider, the ticket sits beside a Chip in panel so people can give without leaving, and the post page uses the same split. The first ticket rewards follow-through (ADR 0013): overdue posters are out, a good record comes first, then first-time posters, then closest to goal. Positive feedback is capped per update, so a pile of kudos can't cancel real 🤨. Reviews also raised contrast on error text and the dark green hover, made the ticket stack visible in dark mode, and held post stories to a readable line length. `DESIGN.md` now describes this look.

### Changed
- Safer chip-in (#78). Logged-out visitors are told to log in before the pay buttons, and logging in or signing up returns them to the post. The amount is remembered while a donor is in their payment app, and after tapping a pay button the panel asks one question: "Sent $20 to $mariag on Cash App?" Without JavaScript the full form stays. A donor with a waiting gift sees that instead of the form. A gift can be recorded for 24 hours after a post closes. "Paid with" replaces "via", a single payment app is preselected, and a plain hint replaces the "$20.00" placeholder.

### Fixed
- Hardening from Impeccable's audit (#77). Errors show styled pages with a way forward, and a stale form returns you to the page with a message. Form errors are focused and announced, and error text no longer pollutes field names. The top bar wraps at 320px and with large text. The packet username is a larger target, and there's a skip link. Any gift shows at least one progress mark, and the row stays visible in high-contrast mode. Long post titles scale down, and the same post sent twice within a minute makes one post.

### Changed
- Complete redesign with Impeccable (#75). Every page moves to the owner-chosen Seed Packet look: a leaf-green shell, flat colour bands for posts (leaf for needs, teal for wants), marigold for primary actions, Bitter and Public Sans (self-hosted), and progress as a growing row of ten marks. The feed becomes a rack of packets, in two columns on phones, and tapping a whole card opens the post. Filters read All, Needs, Wants, the pay-app buttons now lead over "I sent it", and My gifts leads with the post title. Earlier surface briefs are replaced by one app-wide brief. Font licenses sit beside the fonts.

### Added
- Follow-through stat on profiles (#28, ADR 0008): "Updated N of M posts", counting posts whose results update is posted or overdue. It's hidden when nothing has come due. Impeccable's finish review also made the update's due date stand out, explained 👍 and 🤨, and showed the 20-character minimum up front.
- Kudos and reactions on results updates (#64, ADR 0008). Any verified user can give Kudos, and people with a confirmed gift on the post can use 👍 or 🤨, which replace each other. Tapping again removes it, and posters can't react to their own update. Kudos and 👍 counts are public, only admins see 🤨 counts, and reactions earn no XP (migration 0009).
- Overdue results updates block new posts (#27, T12). While one is overdue, creating a post sends you to that post with an explanation, and posting the update lifts the block right away. It's worked out from dates, so a missed job can't block or unblock anyone. The post page shows when an update is overdue. `flask posts remind` emails the poster once on day 3 and once on day 6 (migration 0008 adds `posts.update_reminders_sent`).
- Results updates (#26, ADR 0008). A closed post with a confirmed gift owes one text note of 20 or more characters, due 7 days after the later of the close and the latest confirmation. The form says receipts are never needed and warns against sharing account numbers or medical details (T14). Notes that read like fundraising are refused. The update shows on the post and everyone who chipped in is emailed once, including anyone confirmed later. There's no editing. A deleted post still owes its update, and deleting a post later scrubs the note but still counts as updated (migration 0007).
- Close a post, and auto-close after 30 days (#65). The poster can close an open post with an inline "Are you sure?" step, and there's no reopening. An open post closes on its own at 30 days, worked out from its date with no cron (migration 0006 adds `posts.closed_at`). A closed post leaves the feed, stops taking gifts, and no longer counts toward the 2-post limit. Gifts already sent can still be confirmed. Open posts show the last full day they're open. Recording a gift on a post that has just closed now explains why it can't count.
- Project foundation: tooling, CI, templates, PRD, ADRs, threat model, and a Flask skeleton with `/health`.
- Render staging blueprint (`render.yaml`) with gunicorn and free Postgres; ADR 0005.
- `User` and `Post` models, Alembic migration 0001, and a `flask seed` command that creates 10 users and 20 posts for local dev (#1). Money is stored as integer cents (ADR 0006).

- Sign up with email verification (#2): CSRF-protected forms (Flask-WTF), hashed passwords, signed 48-hour verification links, a resend option, and a `verified_required` guard. Emails are logged to the console unless `MAIL_SERVER` is set (ADR 0007).
- Mobile-first base layout and stylesheet.
- Log in and log out (#3). More than five failed logins for one account from one IP, or twenty from one IP overall, within 15 minutes returns 429. Attempts are stored in a new `login_attempts` table (migration 0002), and `next` redirects must be local.
- Profile (#4): self-reported city and state (no GPS), plus Cash App, Venmo, and PayPal handles, validated and normalized in `app/payment_links.py`. Changing a handle emails a notice to the account. Public profile at `/u/<username>`.
- Create a post (#5): a Want or Need with a goal up to $1,000 (parsed to cents in `app/money.py`), at most 2 open or in-review posts per user, a payment handle required, and Community Rules (`/rules`) accepted before the first post. Text matching the fundraising keyword list (`app/moderation.py`) goes to `pending_review`.
- Feed of open posts at `/` (#6): newest first, All/Wants/Needs filter, 20 per page, and cards with a kind chip, poster, region, goal, and progress bar. Progress counts confirmed gifts only (ADR 0004).
- Post detail page `/posts/<id>` (#7): story, poster and region, goal, progress, and the poster's payment handles while the post is open. Pending-review and removed posts return 404 to everyone except the owner and admins. Feed cards and new posts link here.

- ADR 0008 (required results updates) and ADR 0009 (leaderboards rank by people helped), threat-model cases T11–T15, new PRD risks and metric, and a product backlog with issues #26–#36 (#25).
- Release roadmap from staging to the App Store (`docs/roadmap.md`) and backlog items PB-12 to PB-19 for the App Store requirements.

- `Donation` model and migration 0003 (#46): a gift's post, donor, amount in cents (capped at $1,000), payment app, and status (`pending`, `confirmed`, `disputed`). Post progress now sums confirmed gifts only (ADR 0004), and `flask seed` adds a few gifts.

- Pay-app buttons on open posts (#43): type an amount once and the Cash App, Venmo, and PayPal buttons open prefilled (`app/static/js/chip-in.js`). Without JS they open the poster's page in each app. Only the poster's apps are shown.

- Record a gift (#45): on an open post, a verified donor who isn't the poster can say "I sent $X via <app>". This saves a `pending` gift and emails the poster. Logged-out visitors get a log-in link. Pending gifts don't move the progress bar until the poster confirms them. A gift can be at most the post's goal, the donor must pick the app they used (tapping an app's pay button picks it), and each donor can have one pending gift per post. Pressing Enter in the amount box doesn't record a gift.
- Confirm or dispute gifts (#44): `/gifts` lists gifts waiting for the poster, each showing its amount, app, donor, post, and date, with Confirm or "Didn't get it". Disputing asks once inline (`?dispute=<id>`, no JavaScript) before acting. The page also lists the gifts you sent with plain statuses: Waiting, Confirmed, Not received. Only the recipient can resolve a gift, and confirming enough to reach the goal marks the post funded. The top bar shows how many gifts are waiting, and long usernames truncate.
- Pending gifts expire after 14 days (#29, T15). That's worked out from the gift's date, with no cron: an expired gift leaves "To confirm" and the badge, can't be confirmed, earns nothing, shows as Expired in "My gifts", and no longer blocks the donor from recording a new gift. `flask gifts remind` emails each poster once about gifts waiting 3 or more days (migration 0004 adds `donations.reminded_at`). Production will run it daily; links use the new `APP_URL` setting.
- 18+ attestation at signup (#30, T13): a required "I'm 18 or older" checkbox. Without it no account is created, and the time it was ticked is stored in `users.adult_attested_at` (migration 0005).
- Delete a post or your account (#31, T14), each with an inline "Are you sure?" step. A post with no gifts is removed. One with any recorded gift loses its story but stays, so donors keep credit and their records; an open post closes, and funded or moderated posts keep their status. Deleting the account needs your password and has the same rate limit as login. It removes or scrubs your posts, anonymizes you as `deleted-<id>`, clears your email, handles, region, and login history, and ends your sessions on every device.
- Design context for Impeccable: `PRODUCT.md` (product truth for design work) and the `/gifts` surface brief in `.impeccable/surfaces/`.

- Beta-ready design polish with Impeccable (#54), keeping the existing colors, themes, layout, and wording:
  - Every form field shows its error state and links it for screen readers.
  - Native controls follow dark mode (`color-scheme`, `accent-color`).
  - Buttons and tabs get hover, focus, active, and disabled states.
  - Selection, caret, placeholder, and link underlines are themed, and money uses tabular figures.
  - Notices use a tint instead of a colored side border.
  - Top-bar links have 44px touch targets at the same height, and flash messages are announced.
  - Owner-approved copy: "donate" wording became gift and chip-in wording, and form errors are written plainly.

- XP and levels (#56): each confirmed gift earns 10 XP, plus 25 the first time you help a new person, and the amount doesn't matter (ADR 0010). Only gifts to verified recipients with accounts at least 3 days old count, and gifts on removed posts don't. Level L starts at 50 × L × (L − 1) XP. The public profile shows the level, an XP bar, and people helped. Everything is computed from confirmed gifts in `app/rewards.py`.

- Weekly giving streak (#58): consecutive Monday-to-Sunday (UTC) weeks with a confirmed gift that counts toward rewards, ending this week or last. The profile shows "N-week streak".

- Badges (#57): First gift, Helped 5, Helped 25, Local hero (3 people in your own city and state), and On a roll (a 4-week streak). They're computed from confirmed gifts that count toward rewards, and only earned badges show on the profile.

- Leaderboards (#59): `/leaders` ranks donors by distinct people helped, with Global / state / city tabs and This week / All time. Only verified donors and recipients whose accounts are 3+ days old count, and a donor→recipient pair over $200 in a week is left out. Your row is highlighted (or listed below the top 20), and a full board links to the feed. The top bar gains Leaders, and Log out moves to the profile page.

### Fixed
- Staging deploys failing since #12 (#23): SQLAlchemy 2.1 defaults `postgresql://` to psycopg 3, but only psycopg2 was installed. The app now depends on `psycopg[binary]` and pins `postgresql+psycopg://` for any Postgres URL scheme.

### Changed
- CSRF tokens last for the browser session instead of one hour, because donors leave for their payment app in the middle of the form (#45).
- README: steps for recreating the staging database before the free tier expires (#33).
- Staging runs `flask db upgrade` before starting gunicorn.
