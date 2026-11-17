# Spike: what makes Tinder and Instagram feel snappy (#220)

Research only, with no app code. The owner wants Yearnly to feel snappy, smooth, and clean, and asked what we can learn from Tinder and Instagram. This doc covers what those two apps do, what Yearnly already does, what fits the one-ticket feed and the How stories, and what doesn't. It ends with candidate stories for the owner to pick.

Sources: how the apps behave in normal use, the current `DESIGN.md` (The Deck, the How stories), `app/static/js/swipe.js`, `how.js`, and `sw.js`. No usage numbers or studies are quoted, because we have none we can stand behind.

## Ground rules this has to respect

- **Nothing pressures people to give.** Snappy means less waiting and less friction, never urgency. No countdowns, no "people are viewing this", no auto-advance that hurries a decision, and no reward for tapping Chip in. Celebration belongs to *confirmed* gifts (ADR 0004), not to the tap that opens a pay app.
- **No business fundraising,** and nothing that sells attention. A paid boost or a "super ask" would be a marketplace for visibility, so it's out.
- **Every gesture keeps a real link** and works without JavaScript and at 360px (DESIGN.md, Do's). Reduced motion gets a fade or nothing.
- **The look stays flat:** no shadows, glow, shimmer, or gradients other than fades into the field (DESIGN.md, Don'ts). Motion is transform and opacity only, so it runs on the compositor while the next page loads.
- **Stack:** server-rendered Flask and vanilla JS (ADR 0003). Each ticket and each story step is its own page, so "instant" mostly means hiding the page load.

## Tinder

| Pattern | What it does | Why it feels fast |
|---|---|---|
| Card stack | The next card is already drawn under the current one, slightly smaller, and grows to full size as the top card leaves. | There's never an empty moment. The next thing is visible before you commit. |
| Swipe physics | The card follows the finger 1:1, rotates around a point below it as it moves sideways, commits past a distance or on a fast flick, and springs back otherwise. | Direct manipulation: the card is in your hand, so the app never seems to "think". |
| Direction stamps | LIKE and NOPE stamps fade in with distance. | Confirms intent before release. |
| Preloading | Photos for the next few cards are fetched ahead. | The card underneath is complete when it's revealed. |
| Buttons | Every swipe has a button twin. | Accessibility and discoverability. |
| Haptics | Taps on key moments (a match) on the native app. | Feels physical, marks the moment. |
| Undo (Rewind) | Brings back the last card. It's a paid feature. | Lowers the cost of a fast swipe. |

## Instagram

| Pattern | What it does | Why it feels fast |
|---|---|---|
| Stories tap zones | Tap the right side for the next item, the left to go back. Swipe sideways to jump to the next person, down to close. | Huge targets, no aiming. |
| Hold to pause | Pressing and holding pauses the story and hides the chrome. | You control the pace of an auto-advancing story. |
| Progress bars | Segmented bars at the top show where you are, and the current one fills. | Shows how much is left, so moving on feels safe. |
| Instant transitions | The next story's media is loaded ahead, and the cut happens with no spinner. A 3D cube turn links one person's stories to the next. | No visible load between items. |
| Skeletons | Gray placeholder shapes, sometimes with a shimmer, while the feed or a profile loads. | The layout shows up at once and fills in. |
| Optimistic UI | The heart fills the moment you tap or double-tap, and a comment appears before the server answers. If the request fails, it quietly rolls back. | The app answers at the speed of the tap. |

## What Yearnly already has

The Deck already does most of Tinder's work. A drag past 8px picks up the card, it tilts up to 4deg, the real neighboring ticket is cloned underneath from a `<template>`, and its photo is decoded ahead of time. The rail glyph lights after 24px. The card commits past 30% of its width or on a 0.5px/ms flick, throws in 180ms, and otherwise settles in 200ms. There's 25% resistance at the end of the pile, a fade with reduced motion, and a `<link rel=prefetch>` for the target. Back is a free undo.

The How stories already have segmented step bars, a 60px swipe, arrow keys, and cross-document View Transitions for the door-to-field morph and the step slide.

**The remaining gap is the page load.** The throw ends with `location.assign()`, so the user waits for a full page and can see a blank or white frame in between. #219 is fixing the flash and timing story steps. Everything below assumes #219 lands first.

## What fits, and what doesn't

### Fits

1. **The card underneath becomes the next page (Tinder stack, Instagram's instant cut).** Give the ticket a `view-transition-name` on both pages so the cut lands on the same card the user just saw underneath, with no reload frame. Add Speculation Rules to prerender Next where the browser supports it (Chromium), and keep the prefetch for Safari and the iOS shell. This is the biggest win, and it mirrors what the story pages already do.
2. **Depth under the card.** Today the neighbor sits underneath at full size. Tinder's cue is that it starts slightly smaller and grows as the top card moves, for example scale 0.96 to 1 tied to drag progress. It's transform only, so it stays within the flat look and needs no shadow.
3. **Tap zones on the How stories.** Tap the right part of the field for Next and the left for Back, ignoring taps on links and example pieces. The stories are three short steps, so it's Instagram's best gesture without its pressure. When the step changes, the step bar fills in about 200ms, which marks place, not progress toward money (DESIGN.md's rule on step bars).
4. **Optimistic reactions.** Kudos, 👍 and 🤨 on results updates are form posts that reload the page today. Send them with `fetch`, update the count and pressed state at once, and roll back with a short message if the request fails. The form stays the no-JS path. This celebrates follow-through, not giving.
5. **Undo for show less (#119).** When swipe-down "show less" lands, a toast like "Showing less Games · Undo" lets a fast swipe be cheap, like Rewind, but free.
6. **Haptics in the iOS shell only.** A light tap when a card commits, and a success pattern when a gift is *confirmed* (yours, or one you confirm as the poster). iOS Safari has no web vibration, so this needs `@capacitor/haptics`, plus a check that the native bridge reaches pages loaded from `server.url`. Never fire a haptic on Chip in or on a pay-app button.

### Doesn't fit

- **Auto-advance and hold-to-pause.** Stories that move on by themselves hurry people. The feed is a person's ask, and the How steps are read at the reader's pace, so nothing auto-advances and there's nothing to pause.
- **LIKE / NOPE stamps.** Yearnly's left is "next", not a rejection of a person. The rail glyph already confirms direction without judging anyone.
- **Paid Rewind, Super Like, Boost.** Undo stays free. Paying to be seen first is a marketplace for attention and drifts toward fundraising for profit. The first ticket stays earned by follow-through (ADR 0013).
- **Double-tap to react on an ask.** A heart on someone's need is engagement bait and suggests support without a gift. Reactions stay on results updates.
- **The cube turn between people.** It's a 3D effect in a flat system and would fight the sideways card.
- **Shimmer skeletons.** The pages are server-rendered and arrive whole, and shimmer is the glow and gradient DESIGN.md rules out. Yearnly's skeleton already exists: the field color holds the ticket while its photo loads. Painting the ground before CSS (#219) covers the rest.
- **Optimistic gifts.** "I sent it" and confirm/dispute stay server-truth. A gift that looks recorded but isn't would break honest credit (ADR 0004). Those buttons can show a pressed state while they submit, but the result comes from the server.
- **Infinite scroll or a vertical feed.** It's against DESIGN.md (one ask per screen) and is what makes feeds feel endless rather than fast.

## Candidate stories for the owner

Each one needs the owner's look through Impeccable before it's Ready (AGENTS.md). They're in the order I'd suggest.

1. **Seamless ticket cut** (after #219). Next and Back land on the card that was showing underneath, with no blank frame. Speculation Rules prerender Next in Chromium, and prefetch stays for Safari and iOS.
   - Given a warm session on a TestFlight build, when I flick to Next, then there's no white or blank frame.
   - With reduced motion it's a fade. Without JS, the links still work.
2. **Stack depth.** The neighbor under the card grows from slightly smaller to full size as I drag, and settles back if I let go. Transform only, and none with reduced motion.
3. **Tap to move through the How stories.** Tap the right part of a step for Next and the left for Back, while links and example pieces keep their own taps. The step bar fills in about 200ms. Nothing auto-advances.
4. **Instant reactions.** Kudos, 👍 and 🤨 respond at once without a page reload, and roll back with a message if the server says no. The no-JS form keeps working.
5. **Undo show less** (folds into #119). Swipe-down show less offers Undo for a few seconds.
6. **Haptics in the iOS app.** A light tap when a card commits, and a success pattern when a gift is confirmed. Never on Chip in or a pay-app button. iOS shell only, with a spike to check the Capacitor bridge on the remote URL first.
