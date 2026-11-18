# App Store listing and review pack (PB-19, #260)

Everything to paste into App Store Connect for Yearnly's first iOS submission, plus what the reviewer needs. Regenerate the screenshots with `pytest -m appstore --no-cov` after any visible change.

## Before submitting (blockers)
These are owner or main decisions. The pack is ready around them.
1. **Card gifts and Guideline 3.2.1(vii).** Apple lets an app skip in-app purchase for person-to-person gifts only if "100% of the funds go to the receiver of the gift." The owner's decision (2026-11-18): no platform fee on any gift, an optional "Support Yearnly" tip on the web only, and no tip or fee in the iOS shell (#265, main then ui). Submit after #265 ships. One question remains for the PB-39 legal review: Stripe's card processing fee still comes out of a card gift (ADR 0016), so check whether Apple accepts that, or whether the donor should cover it in the app.
2. **A support URL.** Apple needs a web page, not just an email. The `/support` page is #264 (main).
3. **Blocking.** Guideline 1.2 requires that users can block abusive users. That's PB-12 (#257), and it has to ship first.
4. **The privacy policy's "Draft, pending legal review" line.** Reviewers read the policy, so finish the legal review (PB-39). This is on the owner's list.
5. **The demo account.** The owner creates it on production (see Review notes). The credentials go only into App Store Connect, never into this repo. This is on the owner's list.

## Listing
| Field | Value |
|---|---|
| Name (30) | Yearnly |
| Subtitle (30) | Chip in on everyday asks |
| Primary category | Lifestyle |
| Secondary category | Social Networking |
| Privacy policy URL | https://yearnly.app/privacy |
| Support URL | https://yearnly.app/support (blocker 2) |
| Marketing URL | https://yearnly.app |
| Copyright | 2026 Yearnly |
| Age rating | 18+ (users must confirm they're 18 or older at sign-up) |

**Promotional text (170):**
Help someone with rent, a bill, or something fun, straight from your own Cash App, Venmo, or PayPal. Only gifts the person confirms count toward your rewards.

**Description:**
> Yearnly is a place for small, everyday asks: rent that's coming up short, a utility bill, groceries, or just a game someone's been wanting. Anyone 18 or older can post a want or a need of up to $1,000, and anyone can chip in.
>
> Giving happens in your own payment app. Pick a person, open their Cash App, Venmo, or PayPal from their post, and send what you like. Yearnly never holds your money.
>
> Once the person confirms your gift arrived, it counts. You earn XP and levels, keep a weekly streak, collect badges, and climb leaderboards ranked by how many different people you've helped, never by how much you spent.
>
> When a post closes, the person who got help says how it went, so you see what your gift did.
>
> Posts are for personal wants and needs only. Business, startup, product, and investment fundraising isn't allowed, and posts that look like it are held for review. You can report any post or person.
>
> Gifts are voluntary and aren't charitable donations or tax-deductible.

**Keywords (100):** `chip in,gift,help,rent,bills,mutual aid,cash app,venmo,paypal,community,wishlist,kindness,giving`

Check this before pasting: the copy never says "charitable donation" (except "aren't charitable donations") and makes no claims about users, totals, or results (PRODUCT.md, "Evidence on Hand").

## Screenshots
The screenshots are in `screenshots/`, generated from the real app on seed data by `tests/e2e/test_app_store.py`.

| Folder | Size | Device class |
|---|---|---|
| `6.7in/` | 1290 × 2796 | 6.7" and 6.9" (upload this set first) |
| `6.5in/` | 1242 × 2688 | 6.5" |

Order: 1 front door, 2 how it works, 3 the feed, 4 a post, 5 Chip in, 6 your gifts and level, 7 leaders. The names on them (maria_g, priya_k, dev_tom, …) are seed accounts, not real people.

## App Privacy (nutrition label)
**Tracking:** none. There are no ads, no third-party analytics, and no tracking cookies.

| Data type | Collected | Linked to the user | Purpose | Where it comes from |
|---|---|---|---|---|
| Contact Info: Email Address | Yes | Yes | App Functionality | Sign-up, verification, and gift emails |
| Contact Info: Name | Yes (optional) | Yes | App Functionality | "Name on your app" when recording a gift (#81). Only the recipient sees it |
| User Content: Photos | Yes | Yes | App Functionality | An optional post photo |
| User Content: Other User Content | Yes | Yes | App Functionality | Posts, results updates, payment handles, reports, and the self-reported city and state |
| Identifiers: User ID | Yes | Yes | App Functionality | Username |
| Financial Info: Payment Info | Card gifts only | Yes | App Functionality | Collected by Stripe Checkout, not by Yearnly |

Not collected: precise or coarse location from the device (the city is typed in), contacts, browsing history, health, and diagnostics. If PB-15's error tracker ships first, add **Diagnostics: Crash Data**.

Login attempts and IP addresses are kept only to stop password guessing. Check with the legal review whether Apple counts that as collected data.

## Age rating answers
- User-generated content: yes, moderated (reports, the admin queue, and the fundraising keyword hold).
- Unrestricted web access: no. Pay-app links leave the app to Cash App, Venmo, or PayPal.
- Gambling, contests, mature themes, violence: none.
- Rating: **18+**, because the Terms and the sign-up attestation require adults (T13).

## Review notes (paste into App Review Information)
> **Demo account:** username `<from App Store Connect>`, password `<from App Store Connect>`. It has a verified email, payment handles, an open post, and one gift waiting to be confirmed.
>
> **What the app is:** people post small personal wants and needs, up to $1,000, and other adults chip in.
>
> **Payments (3.2.1(vii)):** gifts go from one person to another in the giver's own Cash App, Venmo, or PayPal. Tapping a pay button on a post opens that app, and Yearnly never receives or holds the money. Giving is optional. Yearnly takes no fee on any gift, and the app has no tips, so the whole gift goes to the receiver. Nothing is unlocked by paying. XP, levels, and badges count *people helped*, not dollars, and are earned only when the receiver confirms a gift.
>
> **User-generated content (1.2):**
> - Every post has "Report this post", and every profile has "Report <name>". Reports go to an admin queue at /admin.
> - Posts that look like business or investment fundraising are held for review before anyone sees them.
> - Users can block another user (PB-12).
> - The Community Rules are linked from every page. Contact: support@yearnly.app.
>
> **Account deletion (5.1.1(v)):** You → Settings → Delete account. It removes the profile, handles, and photos, and scrubs posts.
>
> **Try it:**
> 1. Log in, then swipe or tap through the feed.
> 2. Tap a post, or "See more", to open it.
> 3. Open a pay app from Chip in, or tap "I sent it" to record a gift.
> 4. On You, confirm the waiting gift.

## Copy audit (2026-11-18)
User-facing templates, emails, and JS say "gift" and "chip in" throughout. The only "charitable donation" is the Terms saying a gift *isn't* one. `donation` appears only in code (model and variable names), never in copy.
