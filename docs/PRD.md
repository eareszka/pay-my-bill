# Product Requirements — Pay My Bill

**Owner:** Emery · **Status:** Draft v0.1 · **Last updated:** 2026-10-27

## Problem
People often need a small amount of help for something ordinary: rent coming up short, a utility bill, or just a video game they want. No platform is built for these small, personal, sometimes silly asks. Crowdfunding sites are built around big campaigns and businesses. Meanwhile, people who would happily chip in a few dollars get nothing back for it: no recognition, no sense of community, no proof it mattered.

## Vision
A feel-good community where anyone can post an everyday want or need, and anyone can help. Helping is visible and celebrated, and the person who got help says thanks.

## Target users
- **Posters:** individuals with small personal wants or needs, up to $1,000
- **Donors:** people who like helping others and enjoy recognition, competition, and gratitude

## Goals (v0.1-alpha)
1. A user can post a want or need and receive help through their own Cash App, Venmo, or PayPal.
2. Donors are rewarded with XP, levels, badges, streaks, leaderboards, kudos, and thank-yous.
3. Business and startup fundraising is kept off the platform.

## Non-goals
- **Fundraising for any business, startup, product, or investment.** This is prohibited.
- Holding, processing, or transmitting money. The app links out to existing payment apps.
- Native iOS and Android apps before v1.0. The PWA comes first.
- Charitable tax receipts or acting as a registered charity.

## Success metrics (closed beta)
- At least 50% of posts receive one or more confirmed donations
- At least 40% of funded posts get a thank-you
- At least 30% of donors give again within 2 weeks
- Under 2% of published posts are removed for violating the fundraising rule

## Scope by release
| Release | Scope |
|---|---|
| v0.1-alpha | Auth, posts, link-out donations with confirmation, XP/levels/badges/streaks, leaderboards, thank-yous, kudos, reports and admin queue, PWA |
| v0.2-beta | Production deploy, closed beta, notifications, fixes from beta feedback |
| v1.0 | Public launch after legal review; possibly an iOS wrapper |

## Risk register
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Fake "I sent it" claims inflate leaderboards | High | Medium | Only confirmed donations count; per donor→recipient weekly cap; account-age gate |
| Scam or fundraising posts | Medium | High | $1,000 ask cap; keyword flag queue; reports; admin removal and bans |
| Payment app deep-link formats change | Medium | Medium | Isolated in `payment_links.py` with its own tests |
| Scope creep | High | Medium | Release scope is frozen here; new ideas go into the backlog |
| Legal exposure (ToS, privacy, harassment) | Low | High | Draft policies; lawyer review before v1.0 |
