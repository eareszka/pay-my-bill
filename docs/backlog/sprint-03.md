# Sprint 3 Backlog: "Giving feels rewarding"

The owner chose rewards for this sprint, XP per person helped, and rewards shown on the profile plus a Leaders page (2026-10-31). Only confirmed gifts count toward anything (ADR 0004), and leaderboards rank by people helped, never dollars (ADR 0009). Rewards are computed from gifts when read, in `app/rewards.py`, with no stored counters. Results updates and kudos move to Sprint 4.

---

### S3-1 XP and levels on profiles · #56 · 3 pts · P1 · epic:rewards
As a **donor**, I want to **see my XP and level grow** so that **helping feels like progress**.
- [ ] Each confirmed gift earns 10 XP, and the first confirmed gift to a new person earns 25 more. Amount doesn't matter.
- [ ] Levels: Level 1 starts at 0 XP, and level L needs 50 × L × (L − 1) XP: 100, 300, 600, 1,000, and so on.
- [ ] The public profile shows the level, an XP bar toward the next level, and people helped.
- [ ] Pending, disputed, and expired gifts earn nothing.

### S3-2 Badges · #57 · 3 pts · P1 · epic:rewards
- [ ] First gift (1 confirmed gift), Helped 5 (5 people), Helped 25 (25 people), Local hero (3 people in your own city), and On a roll (a 4-week streak).
- [ ] Earned badges show on the public profile. Unearned ones don't.

### S3-3 Weekly giving streak · #58 · 2 pts · P2 · epic:rewards
- [ ] The streak counts consecutive weeks (Monday to Sunday, UTC) with at least one confirmed gift, ending this week or last week.
- [ ] The profile shows "N-week streak" when N ≥ 1.

### S3-4 Leaderboards by people helped · #59 · 5 pts · P1 · epic:leaderboards
As a **donor**, I want to **see where I rank** so that **I'm motivated to help more people**.
- [ ] `/leaders` ranks donors by distinct people helped, with Global, State, and City tabs (the viewer's own region; logged-out visitors see Global) and This week / All time.
- [ ] Only confirmed gifts from verified donors whose accounts are 3 or more days old count (T2). A donor→recipient pair over $200 in one week is left out for that week (T11).
- [ ] The top 20 show. A logged-in viewer outside the top 20 sees their own rank below the list.
- [ ] A "Leaders" link sits in the top bar.

---

## Wireframes (phone width, 360px)

```
Public profile                    /leaders
+----------------------------+    +----------------------------+
| maria_g · Tampa, FL        |    | Leaders                    |
| Level 4                    |    | [Global][FL][Tampa]        |
| [=====-----] 340/600 XP    |    | [This week | All time]     |
| 12 people helped           |    | 1  dev_tom     23 people   |
| 3-week streak              |    | 2  kayla.r     19 people   |
| [First gift][Helped 5]     |    | ...                        |
| Cash App  $mariag          |    | You: #31 · 4 people        |
+----------------------------+    +----------------------------+
```
