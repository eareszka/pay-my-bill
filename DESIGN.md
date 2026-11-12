---
name: Pay My Bill
description: One person's ask owns the screen. Flick sideways through people, flick back, and chip in with one tap.
colors:
  void: "#0a0a0a"
  slate: "#1e2026"
  on-void: "#ffffff"
  on-void-muted: "#a7aebb"
  need: "#b8300f"
  want: "#2445c8"
  bg: "#f3f4f7"
  surface: "#ffffff"
  ink: "#121316"
  muted: "#4a5260"
  line: "#dfe2e8"
  edge: "#8a919d"
  action-bg: "#121316"
  action-fg: "#ffffff"
  action-hover: "#2a2f39"
  good: "#12784a"
  good-tint: "#dcf1e6"
  bad: "#c4302b"
  bad-text: "#b0261f"
  bad-tint: "#fbe3e1"
  info-tint: "#e6e8ee"
  mark-empty: "#dfe2e8"
  surface-dark: "#17181c"
  ink-dark: "#f2f3f5"
  line-dark: "#2a2f39"
  edge-dark: "#6b7380"
  action-hover-dark: "#d9dce2"
  good-dark: "#3ecf8e"
  good-tint-dark: "#12301f"
  bad-dark: "#ff6b61"
  bad-text-dark: "#ff8a82"
  bad-tint-dark: "#3a1714"
typography:
  display-hero:
    fontFamily: "League Gothic, Arial Narrow, sans-serif"
    fontSize: "clamp(3.25rem, 15vw, 4.75rem)"
    fontWeight: 400
    lineHeight: 0.92
    letterSpacing: "0.005em"
  display:
    fontFamily: "League Gothic, Arial Narrow, sans-serif"
    fontSize: "clamp(2.5rem, 11vw, 3.25rem)"
    fontWeight: 400
    lineHeight: 0.95
    letterSpacing: "0.01em"
  brand:
    fontFamily: "League Gothic, Arial Narrow, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "0.02em"
  title:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  figure:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1
    fontFeature: "tnum"
  label:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 700
    lineHeight: 1.2
rounded:
  hairline: "2px"
  sm: "6px"
  md: "8px"
  tab: "12px"
  panel: "14px"
  stage: "18px"
  round: "50%"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "28px"
components:
  button-primary:
    backgroundColor: "{colors.action-bg}"
    textColor: "{colors.action-fg}"
    rounded: "{rounded.md}"
    padding: "10px 18px"
    height: "46px"
    typography: "{typography.body}"
  button-primary-hover:
    backgroundColor: "{colors.action-hover}"
  button-primary-stage:
    backgroundColor: "{colors.on-void}"
    textColor: "{colors.void}"
    rounded: "{rounded.md}"
    padding: "10px 18px"
    height: "46px"
  button-primary-stage-hover:
    backgroundColor: "{colors.action-hover-dark}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "10px 18px"
    height: "46px"
  button-danger:
    backgroundColor: "{colors.bad}"
    textColor: "{colors.on-void}"
    rounded: "{rounded.md}"
    padding: "10px 18px"
    height: "46px"
  button-danger-hover:
    backgroundColor: "{colors.bad-text}"
  chip-in-tab:
    backgroundColor: "{colors.on-void}"
    textColor: "{colors.void}"
    rounded: "{rounded.tab}"
    padding: "15px"
  chip-in-tab-hover:
    backgroundColor: "{colors.info-tint}"
  ticket-need:
    backgroundColor: "{colors.need}"
    textColor: "{colors.on-void}"
    typography: "{typography.display-hero}"
    padding: "64px 84px 18px 18px"
  ticket-want:
    backgroundColor: "{colors.want}"
    textColor: "{colors.on-void}"
    typography: "{typography.display-hero}"
    padding: "64px 84px 18px 18px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "11px 13px"
    height: "48px"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "18px 16px"
  nav-bar:
    backgroundColor: "{colors.void}"
    textColor: "{colors.on-void-muted}"
    height: "64px"
    typography: "{typography.label}"
  nav-bar-active:
    textColor: "{colors.on-void}"
  rail-glyph:
    textColor: "{colors.on-void}"
    rounded: "{rounded.round}"
    size: "52px"
    padding: "12px"
  rail-glyph-lit:
    backgroundColor: "{colors.on-void}"
    textColor: "{colors.void}"
  meter:
    backgroundColor: "{colors.mark-empty}"
    rounded: "{rounded.hairline}"
    height: "4px"
---

# Design System: Pay My Bill

## Overview

**Creative North Star: "The Color Cut"**

The app is a black frame around one person. The shell (top bar, bottom nav, feed stage, post page) is void black, and inside it a single ask fills the screen as a saturated color field with its title set huge in condensed uppercase. You move through people sideways: drag left for the next ask, drag right to go back, and the neighboring ask's color is already waiting underneath, so every move reads as a cut from one field to the next rather than a scroll. White is the only interface ink on the stage. The one money action, Chip in, is a white filled tab that travels with the person.

Away from the stage, the working pages (Gifts, Leaders, profile, forms, admin, legal) are quiet and dense. They follow the system color scheme: cool paper and white panels in light, near-black panels in dark. They share the same two typefaces, the same inverse filled button, and the same hairline language. Lists are hairline rows, progress is a single hairline meter, and states are a small shape plus a word. There are no shadows, glass, or glow, and no gradient except the scrim that keeps white text legible at the foot of a color field (plus the fades from the photo mosaic into the field's own color on the home doors and the story steps).

The system is built for a phone held in one hand. It works at 360px without horizontal scroll and works without JavaScript, because every gesture has a real link behind it. At 960px and wider, the nav moves up into the bar, and the feed card takes the post page's shape: a wide landscape ask joined to a 400px Chip in panel, with big Back and Next buttons outside it. On a monitor nobody has to drag.

**Key Characteristics:**
- Void-black shell that is always dark: top bar, bottom nav, feed stage, and post page.
- One full-bleed color field per ask (Need or Want) under a bottom scrim, with white type only.
- League Gothic uppercase for titles, set huge and tall. Public Sans for everything else.
- Inverse filled primary (ink on light, white on dark), outlined secondary, and tomato only for errors and destructive acts.
- Hairline meter, hairline rows, and Lucide 2px line icons.
- Sideways gestures with a way back: left = next, right = back, each mirrored by a labeled rail button.

## Colors

A monochrome shell (void, ink, white, cool grays) carries the interface, and saturated category fields carry the people.

### Primary
- **Need Ember** (need): the full-bleed field behind a Need ask on the feed card and the post-page hero. It holds white text at about 6:1.
- **Want Cobalt** (want): the field behind a Want ask in the same places. It holds white text at about 7.6:1.

These two are provisional category colors. Story #119 replaces them with per-category fields, which must keep white text at 4.5:1 or better under the scrim.

### Neutral
- **Void** (void): the shell (top bar, phone bottom nav, feed stage, and the page behind the post on stage pages) and the dark-mode page background. It is also the text color on white controls set on void.
- **Slate** (slate): the active nav item's fill on desktop, the nav's top border, and dark-mode info notices.
- **Pure White** (on-void): all text, glyphs, the Chip in tab, and lit rail glyphs on the stage and fields.
- **Fog Gray** (on-void-muted): inactive nav labels and secondary text on void, and the dark-mode muted text.
- **Cool Paper** (bg): the light-mode page background, and the background of inputs inside panels.
- **Panel White** / **Panel Night** (surface / surface-dark): panels, inputs, and the rewards block.
- **Ink** / **Ink Light** (ink / ink-dark): body text, focus rings, selected tabs, and meter fill.
- **Muted Slate** (muted): hints, metadata, ranks, and counts.
- **Hairline** (line / line-dark): row dividers, tab underlines, and section rules.
- **Edge** (edge / edge-dark): input and secondary-button strokes, and the scrollbar thumb.

### Status
- **Follow-through Green** (good, good-tint): confirmed state marks, success flashes, the "you" row on Leaders, pressed reactions, and badges. In dark mode it shifts to good-dark.
- **Tomato** (bad, bad-text, bad-tint): errors, invalid fields, disputed marks, error flashes, and the destructive button. In dark mode it shifts to bad-dark and bad-text-dark.

### Named Rules
**The White Ink Rule.** On the stage and on any color field, white is the only interface ink: text, glyphs, the Chip in tab, and focus rings. Nothing colored sits on a colored field.

**The Tomato Is Trouble Rule.** The bad family appears only for errors, disputed gifts, and destructive actions. It is never decoration, never a category, and never the Chip in color.

**The Always-Void Stage Rule.** The shell and any page that carries an ask's field stay dark whatever the system setting. Ordinary pages follow `prefers-color-scheme`, and the stage forces the dark token set.

## Typography

**Display Font:** League Gothic 400 (with Arial Narrow, sans-serif)
**Body Font:** Public Sans 400 and 700 (with system-ui, -apple-system, Segoe UI, sans-serif)

**Character:** A tall, condensed poster face shouts the ask, and a plain civic sans does all the explaining. The contrast in width and weight does the hierarchy work, so no third face or decorative weight is needed.

### Hierarchy
- **Display Hero** (League Gothic 400, clamp 3.25 to 4.75rem, line-height 0.92, uppercase): the ask's title on the feed card. On the post-page hero it runs clamp 3 to 4.5rem, and 5rem at 960px and wider.
- **Display** (League Gothic 400, clamp 2.5 to 3.25rem, line-height 0.95, uppercase): page titles (Gifts, Leaders, Ask for a hand), the empty-stage title, and the level on the profile.
- **Brand** (League Gothic 400, 1.75rem, uppercase): the "Pay My Bill" wordmark in the top bar.
- **Title** (Public Sans 700, 1.125rem, line-height 1.3): section titles such as Chip in, My gifts, and Results update.
- **Figure** (Public Sans 700, 1.75rem, tabular numerals): raised amounts and gift amounts. It grows to 2rem in the post hero and the side panel.
- **Body** (Public Sans 400, 1rem, line-height 1.5): everything else. Post stories run at 1.0625rem and max 68ch.
- **Label** (Public Sans 700, 0.75rem): nav and rail labels and the deck count.

### Named Rules
**The Two Voices Rule.** League Gothic is only for titles and the wordmark, always uppercase. Every sentence, label, number, and control is Public Sans. Don't use a system face for display.

**The Tabular Money Rule.** Every amount, count, rank, and badge number uses tabular numerals.

## Layout

The layout is mobile first and single column. Ordinary pages sit in a 640px container with 16px padding (28px top and bottom at 960px and wider). Rhythm comes from 8, 12, and 16px gaps inside forms and panels, 18px panel padding, and 28px between major desktop columns.

On phones, the top bar is 52px tall and the nav is a fixed 64px bar at the bottom (plus the safe-area inset) with four icon-over-label items (Feed, Post, Leaders, and the signed-in username in place of "You"; admins also get Admin). The feed stage fills the height between the two bars (minimum 520px). Inside it, the All, Needs, and Wants tabs are centered at the top, the title sits mid-screen, and the foot holds meta, a three-line story, amounts, and the meter. The rail (Back, Next, and the count) sits at the right edge, and the full-width Chip in tab is at the bottom.

At 960px the nav moves into a 60px top bar as icon-beside-label items, centered within 1120px. The feed becomes one wide card, centered within about 1240px: the ask (up to 660px wide, `min(620px, 100dvh - 230px)` tall, 460px minimum) joined to a 400px Chip in panel on surface, with 18px outer corners. The tabs sit centered above it. Back and Next are 60px outlined circles in 88px gutters outside the card, and the count with an "← → to move" hint sits centered below. The title rests just above who and where, as on the post hero. The on-card Chip in tab is hidden because the panel replaces it. Dragging still works but nothing depends on it, and a click or arrow key plays the same 180ms slide. The post page becomes a fluid story column beside a 400px side panel. Below 380px, the card's right padding tightens to 76px so the title clears the rail. The body clips horizontal overflow, so a thrown card never adds a sideways scroll.

## Elevation & Depth

The system is flat. Depth comes from tonal layering (void, then the color field, then white controls) and, during a drag, from the real neighboring ask sitting underneath the one in your hand. The only soft shadow is a legibility aid on the rail glyphs over bright fields, and it disappears when a glyph lights.

### Shadow Vocabulary
- **Glyph lift** (`filter: drop-shadow(0 1px 2px rgb(0 0 0 / 0.45))`): only on unlit rail glyphs over a color field.

### Named Rules
**The Scrim Only Rule.** The one gradient is the bottom scrim on a color field (transparent to 40% black over the lower half on cards, and over the lower 60% on the post hero). Its one exception is the photo fade, on the home doors and on the story step band, which runs from the photos to solid field under the scrim and only ever fades to the field's own color, never to black or another hue. No other gradients, glass, glow, or box shadows.

## Shapes

Corners are gentle and scale with the size of the object: 2px on the meter, 6px on badges, 8px on buttons, inputs, flashes, and desktop nav items, 12px on the Chip in tab, 14px on panels, and 18px on the desktop stage and post hero. On phones the stage and hero bleed edge to edge with no corners. Rail glyphs sit in 52px circles that fill white when engaged. Borders are 1px hairlines for structure, 1.5px for control strokes, and 2px for invalid fields and tab underlines.

## Components

### Buttons
Plain and confident. There is one inverse fill, and everything else is drawn in outline.
- **Shape:** gently rounded (8px), at least 46px tall, padding 10px 18px, Public Sans 700.
- **Primary:** ink fill with white text on light pages, and white fill with void text on dark pages and the stage. Hover shifts the fill one step (action-hover). Pressing scales it to 0.98.
- **Secondary:** transparent with a 1.5px edge stroke and ink text. Hover darkens the stroke to ink. The Cash App, Venmo, and PayPal buttons are secondary when "Chip in instantly" sits above them, and primary when they're the only way to pay.
- **Danger:** a tomato fill used only for confirmed destructive acts such as deleting a post. Its text is white on light pages and void on dark.
- **Disabled:** 50% opacity with a not-allowed cursor.
- **Focus:** a 2px ink outline offset by 2px everywhere (white on void).

### Chip in Tab
The money action rides on the ask. It is a full-width white tab with a 12px radius, 15px padding, void text at 1.0625rem 700, and 18px margins from the field's edges. Hover is #e6e8ee. It links to the post's Chip in section, and on desktop the side panel replaces it.

### State Marks
State is a shape and a word, never a pill. A 10px ring with 2px stroke precedes a 0.875rem 700 label. Confirmed is a filled green dot, disputed is a filled tomato square with tomato text, expired is a filled gray dot, and waiting is an empty ring.

### Panels
- **Corner Style:** 14px.
- **Background:** surface (white in light, #17181c in dark). Inputs and notices inside a panel drop to the page background.
- **Shadow Strategy:** none.
- **Internal Padding:** 18px 16px with 12px gaps.
- On the desktop post page, the side panel loses its fill and padding and sits directly on void. On the desktop feed it is the right half of the card: surface fill, 28px padding, and the card's right-hand corners.

### Inputs / Fields
- **Style:** a 1.5px edge stroke, 8px radius, 11px 13px padding, at least 48px tall (textareas 128px), with a bold label above and a 0.875rem hint below.
- **Hover / Focus:** the stroke turns ink, and focus adds a 2px ink outline offset by 1px.
- **Error:** a 2px tomato stroke, with the hint swapped for a bold bad-text message.

### Navigation
- **Phone:** a fixed void bar at the bottom with Lucide 24px icons over 0.75rem 700 labels in fog gray. The current page turns white and its icon stroke thickens to 2.5. A white count badge on You marks gifts waiting to be confirmed. You opens your own profile, where Gifts now lives.
- **Desktop (960px and wider):** the same items, inline in the top bar with 20px icons and 0.9375rem labels. The current page gets a slate fill with 8px corners.
- **Logged out:** the top bar carries one white filled button (void text, 36px tall, 6px 14px padding, hover #d9dce2) after the nav. It is Sign up, opening plain `/signup`, on every page but the sign-up page, where it becomes Log in and keeps `next`. At 960px and wider the nav hides its duplicate Sign up text link, and on the sign-up page its Log in link too. Phones keep the Sign up tab in the bottom nav. The wordmark links to the home page.
- **Tabs:** text tabs with a 2px underline on the current tab (white on the stage, ink elsewhere) and muted inactive tabs over a hairline.

### Lists
Dense hairline rows with no cards inside cards. Gift and leader lists are bounded top and bottom by 1px lines, with 1px dividers between rows and 12px row padding. Titles are bold, amounts are right-aligned and tabular, and metadata wraps in muted 0.9375rem. Leaders use a three-column subgrid (rank, name, people).

### The You Page
Your own profile is the home for your stuff (#132). The header is your name in Display with an outlined Settings button on the right, your region, the rewards panel, and your handles. Below, text tabs (real links) switch between **Posts** and **Chipped in**. Posts starts with To confirm when gifts are waiting, then your posts as hairline rows: the bold title, "$X of $Y" on the right, the hairline meter while open, and "Need · " plus one state mark that says what's next (Open until a date, Update due by a date, Update overdue as the disputed mark, Funded, In review, Closed), with small Post update, Edit, and Delete links. Chipped in lists your gifts with their state marks. Visitors see the header, handles, and public posts only, never what you gave. Settings (`/profile`) is a form page with a "← Your profile" link.

### Meter
The single progress device. It is a 4px hairline track with 2px corners and an ink fill to the percentage. On a color field it becomes a 30% white track with a white fill, and 3px tall on the card. In forced-colors mode it is drawn in CanvasText.

### The Deck (signature)
One ask per screen, with a real link for each move. Dragging past 8px picks up the card. It follows the finger with a tilt of up to 4deg, and the neighboring ask's field is revealed underneath. After 24px of travel, the rail glyph for the target lights (white disc, void glyph, scale 1.08). A release past 30% of the card's width, or a flick faster than 0.5px/ms, throws it off the screen in 180ms with `cubic-bezier(0.4, 0, 1, 1)` and follows the link. Otherwise it settles back in 200ms with `cubic-bezier(0.16, 1, 0.3, 1)`. With no neighbor, the card gives at 25% resistance. With reduced motion, the card fades instead of moving (120ms). Gestures: left = next, right = back, and down = show less arrives in #119.

### Photo State
A post may carry one poster photo (ADR 0015). On the feed card it fills the field edge to edge (`object-fit: cover`) under a deeper scrim: 45% black at the top for the tabs, clear through the middle, and 82% black at the foot for the words. The title drops to sit just above the foot, so the photo's middle stays clear. On the post page the color-field header grows to `min(72vh, 600px)` (520px on desktop), with the photo behind it and a scrim to 82% at the foot. The ask's color stays underneath while the photo loads. A post with no photo is complete and never shows an empty frame.

### The Home Page
The logged-out front door at `/` (#120) is just two doors, and each opens its own story, one step per server-rendered page. The pages are always void, and the feed itself lives at `/feed`.
- **Doors:** two linked fields, Want Cobalt "I want to help" and Need Ember "I need a hand", each with the bottom scrim. A door carries one League Gothic line at Display Hero size, a 1.0625rem sentence (34ch max), and a bold "See how it works" with a 20px arrow that slides 4px on hover. There is deliberately no small label above the line: the craft floor bans eyebrows, so the line itself names the door. Phones stack them full bleed, each about half the viewport tall (260 to 420px). At 960px they sit side by side as 18px-cornered fields with a 16px gap, as tall as the viewport less the bar (420 to 640px). Focus is a white 2px outline inset 6px.
- **Door photos** (owner's Impeccable pick "Tinted Mosaic", 2026-11-11): each door can carry a mosaic of real post photos across its top. Photos are grayscale with contrast 1.1, multiplied into the door's own field color inside an isolated layer, so they read as the field rather than as pictures. Phones tile 3 across at 48% of the door's height; from 960px it is 3 by 2 at 62%. Seams are 3px. A fade to solid field (solid by 50% of the door on phones, 62% from 960px) sits under the bottom scrim, so the words always sit on solid field. A door shows six photos or none. The help door takes the six newest open asks with photos and the ask door the six newest funded asks, only from verified, unbanned, non-deleted accounts with no report ever on the account or any of its posts (`app/door_photos.py`). The ask door's sentence adds "These asks got there." only when it shows photos. The mosaic is `aria-hidden` with `alt=""` on every tile, and tiles 4 to 6 lazy-load, so phones never fetch the row they hide. From 960px the two doors share subgrid rows, so the headlines and links line up whatever length the sentences run.
- **Step photos** (owner's Impeccable pick "Photo Band", 2026-11-11): every story step carries three of its door's six photos (the help story the open asks, the ask story the funded ones) in a band across the top of the field, with the same grayscale, contrast 1.1, multiply into the field, and 3px seams as the doors. Steps alternate between photos 1 to 3 and 4 to 6, so neighboring steps never show the same ones and step 1 matches the tiles the phone door shows. On phones the band is 44% of the field, with a fade from transparent at 8% to solid field at 40%. From 960px the band is 52%, the fade runs 22% to 50%, and its columns are `1fr 1fr calc(400px + 40px + 28px)`, so the last seam falls in the gap left of the example column. The band is `aria-hidden` with `alt=""` on every photo, and a story shows no photos when its door has fewer than six. The doors and the steps share one macro, `app/templates/_mosaic.html`.
- **Promise line:** a plain void line under the doors, with the money promise in bold white and the rest in fog gray.
- **Stories:** `/how/help` (four steps) and `/how/ask` (three), one step per page at `/how/<path>/<n>`. One field in the story's color fills the screen under the bar: a row of 3px segmented step bars (35% white, white through the current step), then the step line in League Gothic (clamp 2.75 to 4.25rem, 5.5rem at 960px and wider) with no label above it, one 1.0625rem sentence (40ch max), and one example piece. At 960px the words and a 400px example column sit side by side (56px gap) in an 18px-cornered field inside the 1240px frame. The step nav at the foot of the field is Back, a tabular "n of N", and Next, all white bold links with 20px arrows. Back from step 1 returns to the doors.
- **The other door:** waits docked as a strip at the foot of every step (72px min, its own field color and scrim, a 1.75rem League Gothic line and "See how asking works" with the sliding arrow; 18px corners at 960px). On the last step it reads "Or see how …", and Next becomes a white filled Sign up to `/signup?from=<story>` (Go to the feed when logged in).
- **Sign-up page** (owner's Impeccable pick "Button Becomes the Form", 2026-11-12): `/signup` is a void stage page for everyone, in a 480px column. "Join in" in League Gothic at Display Hero size, one on-void-muted sentence (40ch max), then the form in a dark surface card with a 1.5px white edge, 16px corners, and 16px 18px padding, and below it "Already have an account? Log in" in muted text with a bold white link. Arriving from a story (`?from=help` or `?from=ask`), a full-width strip in that story's color and scrim sits sticky at the foot, above the phone nav (24px from the bottom at 960px): 56px min, a 20px back arrow and "Back to how helping works" (or asking), linking to that story's last step. The strip survives a rate-limited (429) submit. Any other `from` is ignored, and plain `/signup` has no strip.
- **Example pieces:** the real app components (the mini ask card, the Chip in panel, the To confirm row, the rewards meter, state marks) under an "Example" tag: 0.75rem 700 white text in a 1.5px white outline with 6px corners. Each piece mirrors the real app in its real state, so the pay step shows filled pay-app buttons with an outlined "I sent it", which is what a post without card gifts shows, and the rewards meter sits at the real XP for one person helped. Example buttons are inert (default cursor, no press). The mini ask card is a 14px-cornered dark surface panel (360px max), like every other example piece, with a 2.5rem League Gothic title, the meter, and a white 12px Chip in tab. It never takes a category color, so the only colors on a step are its own field and the other door's strip (owner, 2026-11-12).
- **The move:** cross-document View Transitions, only under `prefers-reduced-motion: no-preference`. The door, the story field, and the docked strip share one name per story (`field-help`, `field-ask`), so the tapped door grows into the field and the other door shrinks into the strip in 460ms on `--ease-out`. The transition group clips its overflow (18px corners at 960px). It holds the field's own color only when both pages carry that field (how.js adds `keep-help` / `keep-ask`), so a field with no partner just fades. The snapshots are unscaled and anchored left bottom, so a growing door never ghosts. The step content (`how-step`) wipes in from the right with `clip-path: inset(0 0 0 100%)` plus 32px over 420ms ease-out while the old step leaves left in 220ms ease-in. Going back reverses both directions. Opening a door or switching stories delays the incoming words 220ms so the field lands first. `how.js` is a blocking head script on the doors, story, and sign-up pages that sets these transition types on `pagereveal` (the doors count as step 0, sign-up from a story as step 99, so Back from it runs the back cut), and maps a 60px horizontal swipe (pointer, non-mouse) and the arrow keys to Back and Next.
- **The handoff:** from the last step to sign-up, the story's white Sign up (`join-card`) grows into the form card in 460ms on `--ease-out`, its group clipped at the button's 8px radius. The old image is centered and fades out from 100 to 220ms, and the new image, anchored left top, fades in over the first 200ms. The step words leave and the page content cuts in (`how-step`), and the story field sinks into the strip (`field-help` / `field-ask`). Field groups stack at z-index 1, under `how-step` and `join-card` at 2, so the button and words always ride in front of the sinking field.
- **Fallback:** with reduced motion or no View Transition support, steps and the handoff are plain page navigations. Without JavaScript every step is still a link, and the stories are complete.

## Do's and Don'ts

### Do:
- **Do** keep the top bar, bottom nav, feed stage, and post page void (#0a0a0a) in both color schemes, and let every other page follow `prefers-color-scheme`.
- **Do** give each ask a full-bleed color field with the bottom scrim and white type, and check that any new category color holds white at 4.5:1 or better.
- **Do** set titles in League Gothic uppercase and everything else in Public Sans, with tabular numerals for money and counts.
- **Do** use the inverse filled button for the screen's main action, and outline everything else.
- **Do** show progress only with the hairline meter, and lists only as hairline rows.
- **Do** use Lucide line icons at a 2px stroke from the `_icons.html` sprite, always with a visible text label.
- **Do** back every gesture with a labeled button and a real link, so the feed works without JavaScript and at 360px with no horizontal scroll.
- **Do** say "gift" and "chip in" in interface copy.
- **Do** label every demo piece of the app "Example" with the outlined tag, and make it mirror the real component and its real state exactly.

### Don't:
- **Don't** use tomato for anything but errors, disputed gifts, and destructive actions.
- **Don't** add box shadows, glass, glow, or gradients other than the field scrim and the photo fades on the home doors and story steps, each into the field's own color.
- **Don't** put colored text or colored controls on a color field. It's white or nothing.
- **Don't** turn state into pills or badges with fills. Use a shape and a word.
- **Don't** add a second progress style for money or goals (rings, segmented bars, or percentages as hero numbers). The segmented step bars on the How stories mark place in a story, never progress toward a goal.
- **Don't** nest cards in panels or lay asks out as a card grid or vertical-scroll feed.
- **Don't** say "donation" or "charity" anywhere in the interface.
- **Don't** invent stats, counts, testimonials, or quotes on marketing surfaces. The proof is the real app pieces, labeled Example.
