# Sprint 4 Backlog: "Follow-through"

The owner chose follow-through for this sprint (2026-11-01): posts can close, posters report back, and people respond. The owner also set the rules in the ADR 0008 amendments on 2026-11-02. Time-based state is computed from dates when read, so a missed job can't block or unblock anyone wrongly. The current look stays, and Impeccable is used for the screens.

---

### S4-1 Close a post, and auto-close after 30 days · #65 · 3 pts · P1 · epic:posts
As a **poster**, I want to **close my post when I'm done** so that **people stop sending gifts I no longer need**.
- [ ] The poster can close an open post with an inline "Are you sure?" step. There's no reopening.
- [ ] An open post closes on its own 30 days after it was created, computed from its date.
- [ ] A closed post leaves the feed, takes no new gifts, and doesn't count toward the 2-post limit.
- [ ] Gifts already sent can still be confirmed after a post closes.
- [ ] An open post shows the date it closes.

### S4-2 Post a results update · #26 · 5 pts · P1 · epic:posts
As a **recipient**, I want to **tell donors how their help was used** so that **they see it mattered**. (ADR 0008)
- [ ] A closed post with at least one confirmed gift owes one update, due 7 days after the later of the close date and the latest confirmation.
- [ ] The poster sees a prompt with the due date on the post page.
- [ ] A note under 20 characters is rejected with a message. There's no photo and no editing.
- [ ] The form says receipts are never required and warns against sharing account numbers or medical details (T14).
- [ ] The update shows on the post, and every donor with a confirmed gift is emailed once.
- [ ] A deleted post still owes its update, which can be posted on the "Deleted post" page. Deleting a post later scrubs the note but still counts as updated.

### S4-3 Block new posts while an update is overdue, with reminders · #27 · 3 pts · P1 · epic:safety
As the **community**, we want **recipients to follow through** so that **people can't collect and vanish** (T12).
- [ ] While an update is overdue, creating a post sends the poster to the overdue post with an explanation.
- [ ] Posting the update lifts the block right away.
- [ ] `flask --app app posts remind` emails the poster once at day 3 and once at day 6 of the 7.
- [ ] Overdue status is computed from dates, not from a job.

### S4-4 Kudos and reactions on results updates · #64 · 3 pts · P2 · epic:rewards
As a **donor**, I want to **respond to an update** so that **the poster knows it landed**.
- [ ] Any verified user can give Kudos. Only people with a confirmed gift on the post can use 👍 or 🤨.
- [ ] One of each per person. Tapping again removes it, and 👍 and 🤨 replace each other.
- [ ] Posters can't react to their own update.
- [ ] Kudos and 👍 counts are public. Only admins see the 🤨 count.
- [ ] Reactions earn no XP, and it all works without JavaScript.

### S4-5 Follow-through stat on profiles · #28 · 2 pts · P2 · epic:rewards
- [ ] A profile shows "Updated N of M posts", counting posts whose update is posted or overdue.
- [ ] The stat is hidden when M is 0.

---

## Wireframes (phone width, 360px)

```
Your open post (S4-1)             Are you sure? (S4-1)
+----------------------------+    +----------------------------+
| Short on rent this month   |    | ...                        |
| [=====-----]               |    | ------------------------   |
| $150 raised of $300        |    | Close this post? It leaves |
| Hours got cut at work...   |    | the feed and stops taking  |
| Chip in                    |    | gifts, and you can't       |
| Open until Dec 2, 2026.    |    | reopen it. You can still   |
| ------------------------   |    | confirm gifts people sent. |
| [Close post] [Delete post] |    | [Yes, close it] [Cancel]   |
+----------------------------+    +----------------------------+

Poster, update owed (S4-2)        Everyone, after it's posted (S4-2, S4-4)
+----------------------------+    +----------------------------+
| This post is closed...     |    | This post is closed...     |
| Short on rent this month   |    | Short on rent this month   |
| $150 raised of $300        |    | $150 raised of $300        |
| Hours got cut at work...   |    | Hours got cut at work...   |
| Results update             |    | Results update             |
| Due by Dec 9, 2026.        |    | Posted Dec 3, 2026         |
| Tell the 3 people who      |    | Made rent on time. Thank   |
| helped how it went.        |    | you all so much.           |
| [                        ] |    |                            |
| Receipts are never needed. |    | [Kudos 4]                  |
| No account numbers or      |    | [👍 2] [🤨]  people who    |
| medical details.           |    | chipped in only            |
| [Post update]              |    |                            |
+----------------------------+    +----------------------------+
```
