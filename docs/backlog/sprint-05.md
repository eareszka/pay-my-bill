# Sprint 5 Backlog: "Ready for real people"

Impeccable's audit and critique (2026-11-03) scored the site 15/20 technically and 21/40 on usability, with no blockers. The owner chose to fix these findings first, then build photos, then the safety work (reports and the admin queue, blocking, Terms and Privacy, and the PWA shell), which moves to later sprints. Screens use the Seed Rack look in `DESIGN.md`.

---

### S5-1 Harden errors, accessibility, and small screens · #77 · 5 pts · P1
- [ ] 400, 403, 404, 405, and 500 errors show a styled page with a way forward.
- [ ] An expired session or stale form sends you back to the page with a clear message, instead of a raw error.
- [ ] Form errors are announced and focused. Field labels don't include error text in their accessible name.
- [ ] The top bar wraps at 320px and with large text, with no sideways scroll.
- [ ] The packet username is a 24px or larger target. Skip link and a named main nav are present.
- [ ] Any gift shows at least one progress mark. The row stays visible in high-contrast mode.
- [ ] Long post titles don't push the pay buttons far down. Double-tapping Post can't create two posts.

### S5-2 Safer chip-in flow · #78 · 5 pts · P1
As a **donor**, I want to **be sure my gift will count before and after I pay** so that **real money never goes uncredited**.
- [ ] Logged-out visitors see "Log in first so this counts" above the pay buttons, and log-in and sign-up return them to the post.
- [ ] The amount and app are remembered in the tab while the donor is in their payment app.
- [ ] After tapping a pay button, the panel asks one question: "Sent $20 to $mariag on Cash App?" Without JavaScript the current layout stays.
- [ ] A donor with a waiting gift sees that on the post before the pay buttons.
- [ ] A gift can be recorded for 24 hours after a post closes (#67, owner decision). After that, the message says why it can't count.
- [ ] Hint text replaces the "$20.00" placeholder.

### S5-3 Trust information · #79 · 3 pts · P1
As a **donor**, I want to **see who I'm sending money to** so that **I can decide with confidence**.
- [ ] The post page shows the follow-through stat, when there is one, and "On Pay My Bill since" a month and year.
- [ ] Profiles list the person's past posts, as the Community Rules promise. Deleted and removed posts aren't listed.
- [ ] Follow-through and posts come before the rewards panel, which is hidden at 0 XP.

### S5-4 Visible rewards · #80 · 5 pts · P1
As a **donor**, I want to **see my progress and know when a gift counts** so that **giving feels rewarding**.
- [ ] The username in the top bar opens your own profile, which links to editing it.
- [ ] Gifts shows a strip with your level, people helped, and streak.
- [ ] When a gift is confirmed, the donor gets one email: "maria_g confirmed your $20. You've helped 3 people." (owner decision).
- [ ] The next visit to Gifts shows a one-time banner with the same news. It's plain, with no casino effects.

### S5-5 Clear disputes · #81 · 3 pts · P1
As a **poster**, I want to **match a gift to my payment app**, and as a **donor**, I want to **know what happened** so that **disputes are fair**.
- [ ] Both gift lists show when each gift was sent.
- [ ] When tapping "I sent it", a donor can add the name shown on their payment app, visible only to that poster (owner decision). The Privacy page must cover it.
- [ ] One wording throughout: "Didn't get it" and "Not received", with no "Dispute".
- [ ] Not received and Expired gifts explain what happened and what to do next.

### S5-6 Password reset · #82 · 3 pts · P1
As a **user**, I want to **reset a forgotten password** so that **I don't lose my account**.
- [ ] Log in links to a reset request. The response is the same whether or not the account exists.
- [ ] A signed link that expires and works once sets a new password.
- [ ] Requests are rate-limited, and the account gets a notice when the password changes.

---

## Wireframes (phone width, 360px)

```
Chip in, after a pay tap (S5-2)     Post page trust (S5-3)
+----------------------------+      +----------------------------+
| Sent $20 to $mariag        |      | ## Short on rent ##        |
| on Cash App?               |      | Need · maria_g · Tampa, FL |
| Name on your app (optional)|      | Updated 1 of 2 past posts  |
| [                        ] |      | On Pay My Bill since Oct   |
| [I sent it]   [Not yet]    |      | == == .. .. .. .. .. .. .. |
+----------------------------+      +----------------------------+

Gifts (S5-4, S5-5)
+----------------------------+
| Level 2 · 3 people helped  |
| 2-week streak              |
| maria_g confirmed your $20.|
| You've helped 3 people.    |
| My gifts                   |
| Short on rent         $20  |
| to maria_g · Confirmed     |
| Sent Nov 3, 2:14 pm        |
+----------------------------+
```
