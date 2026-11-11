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

### S5-7 Bulletin board and the top spot · #85 · 5 pts · P1
The owner found the rack too cluttered and chose a bulletin board with no thumbtacks that shows one ticket at a time, with the first ticket as a reward for follow-through.
- [ ] Cork ground, wood top bar, and plain square tickets. Every page moves to this look.
- [ ] The feed shows one large ticket with the stack behind it, a Chip in tab, and Next ticket, with no scrolling list.
- [ ] Tickets show a title, short story, and amount, with who and where on the post page.
- [ ] On wide screens, the ticket sits beside a Chip in panel, and the post page uses the same split (owner's choice).
- [ ] The first ticket follows ADR 0013: overdue posters are out, a good record comes first, then first-time posters, then closest to goal.

---

### S5-8 Swipe through the pile · #90 · 3 pts · P1
The owner sees the feed as swiping through mail and bills, like Tinder except you can go back. Added mid-sprint by the owner, with motion only and no change to the approved look.
- [ ] Swiping left shows the next ticket, and swiping right shows the previous one, with the real post already underneath and no blank stage. On the first ticket, a right swipe springs back.
- [ ] Letting go early settles the ticket back. Scrolling still works over the ticket, and a drag never opens the post or Chip in.
- [ ] Back, Next ticket, and the arrow keys play the same motion, and the arrow keys do nothing while typing.
- [ ] Swiping never gives, passes on, or hides a post.
- [ ] Reduced motion gets a quick fade. Without JavaScript, the links work as before.

### S5-9 New look: the card stack · #118 · 8 pts · P1
The owner wants the app to stop looking AI-made and to read as one simple system on phone and desktop, swiping through people's wants and needs like a dating app, except you can go back. Replaces the cork board through Impeccable; the owner picks the direction. Folds in PB-32 and settles PB-26.
- [ ] Every page uses the new world, and the feed is a card stack: one card at a time with the real next card underneath, left for next, right for back.
- [ ] Motion is fast (250ms or less), readable, and defined once. Dragging shows where the card will go. Reduced motion gets a fade.
- [ ] The top bar reads feed, Post, Gifts, Leaders, profile. Log out moves to the profile, and Rules, Terms, and Privacy sit in the footer. Phone cards say Need or Want in words.
- [ ] Works at 360px without horizontal scroll, in light and dark, and without JavaScript.
- [ ] Ends with the Impeccable finish review and a new `DESIGN.md`.

### S5-10 Categories and show less · #119 · 5 pts · P1
As a **donor**, I want to **see less of a kind of post I don't care about** so that **the stack shows me what I'd chip in on**. Amends ADR 0013 in a new ADR.
- [ ] Posters pick a category from the list the owner confirmed on 2026-11-11: Rent and housing, Bills and utilities, Groceries and food, Car and transport, Health, Kids and school, Fun and games, and Other. Existing posts become Other.
- [ ] Swiping a card down, or its Show less button, moves that category later in my stack. It never hides a post, and the first ticket stays the follow-through pick.
- [ ] I can undo right away and later from my profile.
- [ ] Logged out, the choice lives in a cookie and joins my account when I log in.

### S5-11 How-it-works home page · #120 · 5 pts · P1
As a **new visitor**, I want to **understand how this works before signing up** so that **I trust it**. The owner chose a scroll-driven story.
- [ ] Logged-out visitors land on a scroll-driven page: someone posts, you chip in through their own app, they confirm, you earn credit and they say thanks. It ends at the sign-up form.
- [ ] Example cards are labeled as examples; no invented stats or testimonials.
- [ ] Reduced motion and browsers without scroll-driven animation get a plain stacked page. The feed is one link away, at `/feed`.

### S5-12 Photo on a post · #122 · 5 pts · P1
As a **poster**, I want to **add a photo of what I need** so that **donors can see it**. The owner chose the full upload: Cloudflare R2, shown right away but reportable, and one photo per post (ADR 0015).
- [ ] The post form takes one optional JPG, PNG, or WebP photo up to 8 MB. Anything else gets a clear message, and the rest of the form is kept.
- [ ] The photo fills the feed card and the post page header, and the words stay readable.
- [ ] Location and camera details are removed before the photo is stored.
- [ ] The poster can remove their photo. People can report an inappropriate photo, and admins can remove just the photo.
- [ ] Deleting a post or account deletes its photos.
- [ ] Local dev seeds some posts with free placeholder photos.

### S5-13 You: my posts and chipped in · #132 · 3 pts · P1
As a **user**, I want **one place to see the posts I created and the posts I chipped in on**, on my phone and on a computer. The owner asked Impeccable to decide the design in the current look (2026-11-11). Builds on #116 (PR #117).
- [ ] "You" in the nav opens my own profile with Posts and Chipped in tabs and a Settings button. Gifts folds into You, and its badge moves there.
- [ ] Posts starts with gifts waiting for me to confirm, then my posts with what comes next (open until, update due, update overdue).
- [ ] Chipped in lists my gifts with their state. Only I see it; visitors see my posts.
- [ ] Old `/gifts` links and emails still work.

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
