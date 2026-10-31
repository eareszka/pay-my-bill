# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
- **Donors (primary):** adults in the US who like helping people and enjoy recognition, friendly competition, and being thanked. They browse on their phones, pick a post, pay the poster in their own payment app, and come back to record the gift. When a design choice helps donors or posters more, donors win.
- **Posters:** adults (18+) in the US with a small personal want or need: rent coming up short, a utility bill, groceries, or just a video game they want. They post, share, check their payment app, confirm what arrived, and say thanks.
- **Admins:** review flagged posts and handle reports.

## Product Purpose
A feel-good community where anyone can post an everyday want or need of up to $1,000 and anyone can chip in. Helping is visible and celebrated, and the person who got help says thanks and shows how it was used. Success in the closed beta: at least half of posts get a confirmed gift, at least 30% of donors give again within two weeks, under 2% of posts are removed for fundraising, and at least 70% of funded posts get a results update within 7 days.

## Positioning
Crowdfunding sites are built for big campaigns and businesses. Pay My Bill is for tiny, personal, sometimes silly asks, and it rewards the people who give: XP, levels, badges, streaks, kudos, and leaderboards ranked by distinct people helped, never by dollars. Credit is honest, because only gifts the recipient confirms count. Money goes straight from the donor's Cash App, Venmo, or PayPal to the poster's; the app never holds it.

## Operating Context
- Used mostly on phones, as a mobile-first web app installable to the home screen (PWA). Later the same site is wrapped with Capacitor for the iOS App Store, keeping its own design rather than adopting native iOS conventions.
- A gift leaves the app: the donor types an amount, opens the poster's Cash App, Venmo, or PayPal prefilled, pays there, then returns to tap "I sent it".
- The poster gets an email, checks their payment app, and confirms or disputes the gift on the Gifts page. Pending gifts don't count until confirmed.
- After a post closes with confirmed gifts, the poster owes a results update within 7 days.

## Capabilities and Constraints
- Built so far: sign-up with email verification, log in and out, a profile with city/state and payment handles, posting a Want or Need, the feed, post pages, pay-app buttons, recording a gift, and confirming or disputing gifts.
- Planned for v0.1: XP, levels, badges, streaks, kudos, leaderboards, results updates, reports and an admin queue, blocking, post and account deletion, Terms and Privacy pages, and the PWA shell.
- Hard rules: goals are capped at $1,000, a user can have at most 2 open posts, business, startup, product, or investment fundraising is prohibited, users must be 18+, region is self-reported city and state only (no GPS), and the app never holds or processes money.
- Wording: gifts are "gifts" or "chipping in", never "charitable donations". App Store rules reserve charity collection for registered nonprofits.
- Stack: Flask, Jinja templates, and vanilla CSS/JS, with no SPA framework (ADR 0003). Every page must work at 360px width without horizontal scroll.
- Undecided: the final product name and domain (backlog #35).

## Brand Commitments
- "Pay My Bill" is a working name; the final name is still open (#35). No logo or brand assets exist yet.

## Evidence on Hand
- None yet. The product is pre-beta with no real users, so there are no testimonials, stats, or press. Future work must not invent any.

## Product Principles
1. **Giving comes first.** Make it quick, clear, and rewarding to help someone; donors are the primary user.
2. **Honest credit.** Only recipient-confirmed gifts count, and recognition rewards people helped, not money spent.
3. **Money never touches the app.** Payments link out to the poster's own payment app.
4. **Small and personal.** Everyday wants and needs, capped at $1,000. Never business fundraising.
5. **Follow-through.** Recipients say thanks and show how the help was used.
