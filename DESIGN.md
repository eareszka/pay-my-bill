---
name: Yearnly
description: One person's ask owns the screen. Flick sideways through people, flick back, and chip in with one tap.
colors:
  shell: "#3a7558"
  shell-deep: "#2f6249"
  on-shell: "#ffffff"
  on-shell-muted: "#e8f2eb"
  on-shell-hover: "#e2eee6"
  want: "#b9dcc3"
  need: "#8fcfc0"
  on-field: "#16261d"
  on-field-muted: "#2f4a3a"
  field-track: "rgb(22 38 29 / 0.2)"
  press: "#2f6249"
  chip: "#ffd166"
  chip-hover: "#f5c04a"
  bg: "#f4f6f0"
  surface: "#ffffff"
  ink: "#16261d"
  deep: "#16261d"
  muted: "#4d5c52"
  line: "#dbe2d8"
  edge: "#86958a"
  action-bg: "#3a7558"
  action-fg: "#ffffff"
  action-hover: "#2f6249"
  good: "#12784a"
  good-tint: "#dcf1e6"
  bad: "#c4302b"
  bad-text: "#b0261f"
  bad-tint: "#fbe3e1"
  info-tint: "#e5ece4"
  mark-empty: "#dbe2d8"
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
  tail: "6px"
  check: "7px"
  radius: "14px"
  panel: "22px"
  bubble: "28px"
  pill: "999px"
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
    rounded: "{rounded.pill}"
    padding: "10px 18px"
    height: "46px"
    typography: "{typography.body}"
  button-primary-hover:
    backgroundColor: "{colors.action-hover}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "10px 18px"
    height: "46px"
  button-danger:
    backgroundColor: "{colors.bad}"
    textColor: "{colors.action-fg}"
    rounded: "{rounded.pill}"
    padding: "10px 18px"
    height: "46px"
  button-danger-hover:
    backgroundColor: "{colors.bad-text}"
  button-bar-signup:
    backgroundColor: "{colors.on-shell}"
    textColor: "{colors.deep}"
    rounded: "{rounded.pill}"
    padding: "6px 14px"
    height: "44px"
  button-bar-signup-hover:
    backgroundColor: "{colors.on-shell-hover}"
  button-way-in:
    backgroundColor: "{colors.action-bg}"
    textColor: "{colors.action-fg}"
    rounded: "{rounded.pill}"
    height: "52px"
    width: "100%"
  chip-in-tab:
    backgroundColor: "{colors.chip}"
    textColor: "{colors.deep}"
    rounded: "{rounded.pill}"
    padding: "15px"
  chip-in-tab-hover:
    backgroundColor: "{colors.chip-hover}"
  ticket-need:
    backgroundColor: "{colors.need}"
    textColor: "{colors.on-field}"
    typography: "{typography.display-hero}"
    rounded: "{rounded.bubble}"
    padding: "64px 84px 18px 18px"
  ticket-want:
    backgroundColor: "{colors.want}"
    textColor: "{colors.on-field}"
    typography: "{typography.display-hero}"
    rounded: "{rounded.bubble}"
    padding: "64px 84px 18px 18px"
  home-door:
    backgroundColor: "{colors.want}"
    textColor: "{colors.on-field}"
    rounded: "{rounded.bubble}"
    padding: "22px 20px 20px"
  story-strip:
    textColor: "{colors.on-field}"
    rounded: "{rounded.bubble}"
    padding: "12px 18px"
    height: "72px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.radius}"
    padding: "11px 13px"
    height: "48px"
  checkbox:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.check}"
    size: "22px"
  checkbox-checked:
    backgroundColor: "{colors.shell}"
    textColor: "{colors.on-shell}"
  radio:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.round}"
    size: "22px"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "18px 16px"
  join-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "16px 18px"
  tab:
    textColor: "{colors.muted}"
    rounded: "{rounded.pill}"
    padding: "8px 16px"
  tab-hover:
    backgroundColor: "{colors.info-tint}"
    textColor: "{colors.ink}"
  tab-active:
    backgroundColor: "{colors.shell}"
    textColor: "{colors.on-shell}"
  feed-tab:
    textColor: "{colors.on-field-muted}"
    rounded: "{rounded.pill}"
    padding: "6px 14px"
  feed-tab-active:
    backgroundColor: "{colors.press}"
    textColor: "{colors.on-shell}"
  nav-bar:
    backgroundColor: "{colors.shell}"
    textColor: "{colors.on-shell-muted}"
    height: "64px"
    typography: "{typography.label}"
  nav-bar-active:
    backgroundColor: "{colors.shell-deep}"
    textColor: "{colors.on-shell}"
    rounded: "{rounded.pill}"
    width: "58px"
    height: "32px"
  rail-glyph:
    textColor: "{colors.on-field}"
    rounded: "{rounded.round}"
    size: "52px"
    padding: "12px"
  rail-glyph-lit:
    backgroundColor: "{colors.press}"
    textColor: "{colors.on-shell}"
  meter:
    backgroundColor: "{colors.mark-empty}"
    rounded: "{rounded.pill}"
    height: "4px"
  meter-on-field:
    backgroundColor: "{colors.field-track}"
    rounded: "{rounded.pill}"
    height: "3px"
  example-tag:
    textColor: "{colors.on-field}"
    rounded: "{rounded.pill}"
    padding: "3px 8px"
---

# Design System: Yearnly

## Overview

**Creative North Star: "The Tip Jar"**

The app is a tip jar on a counter: small gifts from passersby, dropped in one at a time. The ground is pale jar glass (bg), the shell (top bar, phone nav, theme color, app icon) is a soft dollar green with white type, and inside it a single ask fills the screen as a light green speech bubble, Want Sage for helping and Need Seafoam for asking, with its title set huge in condensed uppercase in dark green ink. You move through people sideways: drag left for the next ask, drag right to go back, and the neighboring ask's field is already waiting underneath, so every move reads as a cut from one field to the next rather than a scroll. The one money action, Chip in, is a marigold tab, the jar's masking-tape label and the one warm note in the world, so giving never blends into the green chrome. There is no black anywhere: the darkest value is a green-black ink (#16261d).

The world is always light. There is no dark mode, and `prefers-color-scheme` is ignored (`color-scheme: light`). The working pages (Gifts, Leaders, profile, forms, admin, legal) are quiet and dense on the same ground with white panels, the same two typefaces, the same green filled button, and the same shapes. Asking and helping are a conversation (#205): an ask speaks from the right as a big soft bubble with one tight bottom-right corner, a helper's panel answers from the left with its tight corner bottom-left, and every button, tab, badge, and meter is a pill. Lists are hairline rows, progress is a single thin meter, and states are a small shape plus a word. There are no shadows, glass, or glow, and no dark scrim. The only gradients are fades into the field's own color: photos dissolve into the solid field so the words always sit on field.

The system is built for a phone held in one hand. It works at 360px without horizontal scroll and works without JavaScript, because every gesture has a real link behind it. Logged out, the front door (the home page and the How stories) has no bar at all: the way in lives on the page. At 960px and wider, the nav moves up into the bar, and the feed card takes the post page's shape: a wide landscape ask joined to a 400px Chip in panel, with big Back and Next buttons outside it. On a monitor nobody has to drag.

**Key Characteristics:**
- A pale jar-glass ground and a soft dollar-green shell with white type. Always light, no black anywhere.
- One light green field per ask (Want Sage or Need Seafoam) with dark green ink and no scrim.
- League Gothic uppercase for titles, set huge and tall. Public Sans for everything else.
- Two speech bubbles: asks speak from the right (a 6px bottom-right corner), helpers answer from the left (a 6px bottom-left corner), and only the big color fields grow a pointed tail.
- A green filled primary, outlined secondary, a marigold Chip in as the one warm note, and tomato only for errors and destructive acts. Every button is a pill.
- A thin pill meter, hairline rows, and Lucide 2px line icons.
- Sideways gestures with a way back: left = next, right = back, each mirrored by a labeled rail button.

## Colors

A green family (ground, shell, two light fields, green-black ink) carries the whole world, with one marigold note for giving and tomato held back for trouble.

### Primary
- **Dollar Green** (shell): the top bar, the phone bottom nav, the browser theme color, the PWA background, and the app icon ground. White on it holds 5.43:1. The same green is the primary button fill (action-bg) with white text, the current text tab's pill, a checked checkbox or radio, and the small wordmark at the top of the logged-out home.
- **Deep Dollar** (shell-deep): the current nav tab's pill (a 58 by 32px pill behind the icon on phones, around the whole item on desktop), the nav's top border, and the primary button's hover. White on it holds 7.08:1.
- **Shell White** (on-shell): the wordmark, current nav labels, the count badge, the label on a current tab pill, the check in a checked box, and the logged-out Sign up button in the bar (hover on-shell-hover).
- **Pale Mint** (on-shell-muted): inactive nav labels on the shell, at 4.74:1.

### Secondary
- **Want Sage** (want): the field behind a Want ask (the feed card, the post hero), the helping story and strip, and both home doors: the front door speaks in one green (owner, #205), so the asking door wears Sage too while its story keeps Seafoam. Ink on it holds 10.6:1.
- **Need Seafoam** (need): the field behind a Need ask and the asking story and strip. Ink on it holds 8.9:1.
- **Field Ink** / **Field Ink Muted** (on-field / on-field-muted): all text, glyphs, focus rings, and the Example tag outline on a field, and the inactive tabs and meta lines there (6.5:1 on Sage, 5.5:1 on Seafoam).
- **Field Track** (field-track): the 20%-ink track under meters and the story step bars on a field, with a deep fill.
- **Press Green** (press): the disc behind a lit rail glyph on a field, with a white glyph, and its focus ring, and the current feed tab's pill with white text.

These two fields are provisional category colors. Story #119 replaces them with per-category fields, which must keep dark ink at 4.5:1 or better.

### Tertiary
- **Marigold** (chip, chip-hover): the Chip in tab on the feed card and its copy on the How stories' example ask card, always with deep text (10.96:1).

### Neutral
- **Jar Glass** (bg): the page background everywhere, the feed stage behind the deck, and inputs and notices inside panels.
- **Panel White** (surface): panels, inputs, the rewards block, the desktop Chip in panel, the sign-up card, and every example piece on a story field.
- **Green-Black Ink** (ink, deep): body text, focus rings, the meter fill, text on Marigold and on white controls set on the shell. It is the darkest color in the system.
- **Moss Gray** (muted): hints, metadata, ranks, counts, inactive tabs, and the front door's "Already have an account?" line.
- **Hairline** (line): row dividers, section rules, and the sign-up card's edge.
- **Edge** (edge): input, checkbox, radio, and secondary-button strokes, the desktop rail circles, and the scrollbar thumb.
- **Info Tint** (info-tint) and **Meter Track** (mark-empty): info flashes and notices and a tab's hover pill, and the empty meter and expired mark.

### Status
- **Follow-through Green** (good, good-tint): confirmed state marks, success flashes, the "you" row on Leaders, pressed reactions, and badges.
- **Tomato** (bad, bad-text, bad-tint): errors, invalid fields, disputed marks, error flashes, and the destructive button.

### Named Rules
**The Dark Ink On Field Rule.** On a Sage or Seafoam field, every word and glyph set on the field itself is green-black ink (on-field, or on-field-muted for secondary lines), never white and never under a scrim. Filled controls on a field are only Marigold (Chip in, deep text), Dollar Green (the primary, such as the last step's Sign up, white text), Press Green (a lit rail glyph or the current feed tab, white), or a white example panel.

**The One Warm Note Rule.** Marigold is Chip in and nothing else: the feed card's tab and its example on the How stories. It never becomes a category, a badge, or decoration.

**The No Black Rule.** No black and no neutral gray-black anywhere. The darkest color is the green-black ink (#16261d). (The `#000` inside a mask-image gradient is an alpha stop, not a rendered color.)

**The Always Light Rule.** There is no dark mode. The root declares `color-scheme: light`, and nothing reads `prefers-color-scheme`.

**The Tomato Is Trouble Rule.** The bad family appears only for errors, disputed gifts, and destructive actions. It is never decoration, never a category, and never the Chip in color.

## Typography

**Display Font:** League Gothic 400 (with Arial Narrow, sans-serif)
**Body Font:** Public Sans 400 and 700 (with system-ui, -apple-system, Segoe UI, sans-serif)

**Character:** A tall, condensed poster face shouts the ask, and a plain civic sans does all the explaining. The contrast in width and weight does the hierarchy work, so no third face or decorative weight is needed.

### Hierarchy
- **Display Hero** (League Gothic 400, clamp 3.25 to 4.75rem, line-height 0.92, uppercase): the ask's title on the feed card. On the post-page hero it runs clamp 3 to 4.5rem, and 5rem at 960px and wider.
- **Display** (League Gothic 400, clamp 2.5 to 3.25rem, line-height 0.95, uppercase): page titles (Gifts, Leaders, Ask for a hand), the empty-stage title, and the level on the profile.
- **Brand** (League Gothic 400, 1.75rem, uppercase): the "Yearnly" wordmark in the top bar. With no bar on the front door, the logged-out home sets it at 1.875rem in Dollar Green as the page's h1.
- **Title** (Public Sans 700, 1.125rem, line-height 1.3): section titles such as Chip in, My gifts, and Results update.
- **Figure** (Public Sans 700, 1.75rem, tabular numerals): raised amounts and gift amounts. It grows to 2rem in the post hero and the side panel.
- **Body** (Public Sans 400, 1rem, line-height 1.5): everything else. Post stories run at 1.0625rem and max 68ch.
- **Label** (Public Sans 700, 0.75rem): nav and rail labels and the deck count.

### Named Rules
**The Two Voices Rule.** League Gothic is only for titles and the wordmark, always uppercase. Every sentence, label, number, and control is Public Sans. Don't use a system face for display.

**The Tabular Money Rule.** Every amount, count, rank, and badge number uses tabular numerals.

## Layout

The layout is mobile first and single column. Ordinary pages sit in a 640px container with 16px padding (28px top and bottom at 960px and wider). Rhythm comes from 8, 12, and 16px gaps inside forms and panels, 18px panel padding, and 28px between major desktop columns.

On phones, the top bar is 52px tall and the nav is a fixed 64px bar at the bottom (plus the safe-area inset) with four icon-over-label items (Feed, Post, Leaders, and the signed-in username in place of "You"; admins also get Admin). The feed stage fills the height between the two bars (minimum 520px), and the ask inside it is an inset bubble, 8px from the top, 10px from the sides, and 12px from the foot. Inside it, the All, Needs, and Wants pill tabs are centered at the top, the title sits mid-screen (at the top, under the tabs, when the ask has no photo, #208), and the foot holds meta, a three-line story, amounts, and the meter. The rail (Back, Next, and the count) sits at the right edge: Back is an outline glyph, Next is the one filled glyph (a 52px Press Green circle with a white arrow, Deep on hover and focus), and its label and the count tuck right under it as one control (#208), and the full-width Chip in pill is at the bottom.

Logged out on the front door (the home page and the How stories), there is no top bar and no nav at all (#196, #205), and the bar height falls to the safe-area inset. Each page carries its own way in: the home page ends on a Sign up pill and a Log in line, and the stories end on Sign up.

At 960px the nav moves into a 60px top bar as icon-beside-label items, centered within 1120px. The feed becomes one wide speech bubble, centered within about 1240px: the ask is its left side (up to 660px wide, `min(620px, 100dvh - 230px)` tall, 460px minimum, 28px left corners and square right corners) joined to a 400px Chip in panel on surface as its right side (28px top-right, the 6px tail corner bottom-right). With no panel, the stage is a whole ask bubble. The tabs sit centered above it. Back and Next are 60px outlined circles in 88px gutters outside the card, and the count with an "← → to move" hint sits centered below. The title rests just above who and where, as on the post hero. The on-card Chip in tab is hidden because the panel replaces it. Dragging still works but nothing depends on it, and a click or arrow key plays the same 180ms slide. The post page becomes a fluid story column beside a 400px side panel. Below 380px, the card's right padding tightens to 76px so the title clears the rail. The body clips horizontal overflow, so a thrown card never adds a sideways scroll.

## Elevation & Depth

The system is flat, with no shadows of any kind. Depth comes from tonal layering (jar-glass ground, then the light field, then white panels and the marigold tab) and, during a drag, from the real neighboring ask sitting underneath the one in your hand. Photos never sit on top of the words: they dissolve into the field behind them.

### Named Rules
**The Field Fade Only Rule.** The only gradients are fades into the field's own color. The feed card photo is masked transparent at 4%, solid from 18 to 30%, and transparent by 58%, and a photo card washes the field (85% field to transparent by 22%) behind the tabs. The post-hero photo is masked solid to 30% and transparent by 62%. The door and step mosaics fade to solid field before the words. Never a dark scrim, a fade to another hue, glass, glow, or a box or drop shadow.

## Shapes

Asking and helping are a conversation (owner, 2026-11-15, #205, "Two Speech Bubbles"). Every container is a soft speech bubble with exactly one tight corner, its tail, and the side the tail is on says who is speaking. Everything you press is a pill.

- **Ask bubble** (28px, with a 6px bottom-right tail corner; 28/28/6/28): the feed ticket (on phones an inset bubble 8px 10px 12px from the stage edge), the post hero (on phones it pulls 6px past the container on each side), and the example ask card on the How stories. Asks speak from the right.
- **Helper panel** (22px, with a 6px bottom-left tail corner; 22/22/22/6): panels (Chip in, forms, To confirm), the rewards block, and the sign-up card. Helpers answer from the left.
- **The desktop feed** is one bubble split in two: the stage is 28/0/0/28 and the side panel 0/28/6/0, so the tail sits at the panel's foot on the right. On desktop the feed panel's inner group and the post page's side group drop their corners and sit flat.
- **Big color fields** (28px bubbles): the home doors, the story fields, and the docked "other door" strips, including the sign-up page's "Back to how … works" strip. Help-side fields take the 6px corner bottom-left and ask-side fields bottom-right. On the home page both doors are Sage, but the tail still follows the door: "I want to help" bottom-left, "I need a hand" bottom-right.
- **Pills** (999px): every button (including the bar's Sign up, the file picker's button, and the front door's 52px way in), the Chip in tab and its example, tabs, the current nav item, the count badge, badge-list items, meters and their fills, the story step bars, and the Example tag.
- **Gentle** (14px): inputs, selects, textareas, flashes and notices, the skip link, the admin photo, and the "you" row on Leaders. Full-bleed flashes on a stage page stay square.
- **Checkboxes and radios** are drawn, not native: 22px, a 1.5px edge stroke on surface, a 7px-rounded box or a round radio. Checked, they fill Dollar Green with a white check or a white 8px dot.
- **Circles** (50%): rail glyphs (52px on a field, 60px outlined on desktop) and the state-mark rings. The disputed mark is a 10px square with 2px corners.

Borders are 1px hairlines for structure, 1.5px for control strokes, and 2px for invalid fields.

### Named Rules
**The Conversation Rule.** An ask's tight corner is bottom-right and a helper's is bottom-left, always 6px, and a bubble has only one tight corner. If you can't say whether a new container is asking or answering, it's a helper panel.

**The Tails On Fields Only Rule.** A pointed tail is a 22 by 14px clip-path triangle in the field's own color, hanging 12px below the tight corner (bottom-left on the help side, bottom-right on the ask side); from 960px it grows to 40 by 26px and hangs 22px below. The tail's box also reaches 6px up into its bubble (a 6px band above the triangle), so the rounded tail corner never leaves a seam beside it. Only the big color fields carry one: the home doors, the story fields, the sign-up bubble, and the docked strips. Tickets, the post hero, panels, and cards keep just the tight corner.

**The Pill Rule.** Whatever you press is a pill: buttons, tabs, and the Chip in tab. **The 44 Rule** (#208): everything you tap is at least 44px tall, because the iPhone app is the target. Pills, tabs, choices, and the bar's buttons are 44px boxes; standalone text links (the footer, Forgot your password?, Report this post, Find someone to help, names in a card's meta) keep their look and get a 44px tap area from vertical padding, offset by a matching negative margin wherever the link is laid out as a box. Badges and meters are pills too. A gift's state is never a pill (see State Marks).

## Components

### Buttons
Plain and confident. There is one green fill, and everything else is drawn in outline. Every button is a pill.
- **Shape:** a pill (999px), at least 46px tall, padding 10px 18px, Public Sans 700.
- **Primary:** Dollar Green fill with white text everywhere, including on a field (the last story step's Sign up). Hover shifts the fill to Deep Dollar. Pressing scales it to 0.98.
- **Secondary:** transparent with a 1.5px edge stroke and ink text. Hover darkens the stroke to ink. The Cash App, Venmo, and PayPal buttons are secondary when "Chip in instantly" sits above them, and primary when they're the only way to pay.
- **Danger:** a tomato fill with white text, used only for confirmed destructive acts such as deleting a post.
- **Way in:** on the logged-out home, a full-width primary 52px tall at 1.0625rem.
- **Disabled:** 50% opacity with a not-allowed cursor.
- **Focus:** a 2px ink outline offset by 2px everywhere; white on the shell bar, field ink on a field.

### Chip in Tab
The money action rides on the ask. It is a full-width Marigold pill with 15px padding, deep text at 1.0625rem 700, and 18px margins from the field's edges. Hover is chip-hover, and focus is a deep outline offset 3px. It links to the post's Chip in section, and on desktop the side panel replaces it.

### State Marks
State is a shape and a word, never a pill. A 10px ring with 2px stroke precedes a 0.875rem 700 label. Confirmed is a filled green dot, disputed is a filled tomato square with tomato text, expired is a filled gray dot, and waiting is an empty ring.

### Panels
- **Corner Style:** a helper panel, 22px with the 6px tail corner bottom-left.
- **Background:** surface. Inputs and notices inside a panel drop to the page background.
- **Shadow Strategy:** none.
- **Internal Padding:** 18px 16px with 12px gaps.
- On the desktop post page, the side panel loses its fill, padding, and corners and sits directly on the ground. On the desktop feed it is the right half of the card: surface fill, 28px padding, and the card's right-hand corners (28px at the top, the 6px tail at the bottom).

### Inputs / Fields
- **Style:** a 1.5px edge stroke, 14px radius, 11px 13px padding, at least 48px tall (textareas 128px), with a bold label above and a 0.875rem hint below. The file picker's field is 14px and its button a pill.
- **Hover / Focus:** the stroke turns ink, and focus adds a 2px ink outline offset by 1px.
- **Error:** a 2px tomato stroke, with the hint swapped for a bold bad-text message.
- **Checkboxes and radios:** 22px with a 1.5px edge stroke on surface, a 7px-rounded box or a round radio. Hover turns the stroke ink, and checked fills Dollar Green with a white check or dot.

### Navigation
- **Phone:** a fixed Dollar Green bar at the bottom with a Deep Dollar top border and Lucide 24px icons over 0.75rem 700 labels in Pale Mint. The current page turns white, its icon stroke thickens to 2.5, and a 58 by 32px Deep Dollar pill sits behind its icon. A white pill count badge with deep text on You marks gifts waiting to be confirmed. You opens your own profile, where Gifts now lives.
- **Desktop (960px and wider):** the same items, inline in the green top bar with 20px icons and 0.9375rem labels. The current page sits in a Deep Dollar pill.
- **Logged out:** the top bar carries one white pill button (deep text, 44px tall, 6px 14px padding, hover on-shell-hover) after the nav. It is Sign up, opening plain `/signup`. The log-in page is a focused form (owner's Impeccable pick, #208): the bar keeps only the wordmark, with no nav and no button, and "New here? Create an account" under the form is the way across. The sign-up page joins the front door (owner, #208): no bar, no nav, no footer. At 960px and wider the nav hides its duplicate Sign up text link, and on the sign-up page its Log in link too. Phones keep the Sign up tab in the bottom nav. The wordmark links to the home page.
- **The front door** (logged out on the home page and the How stories, #196, #205): there is no top bar, no nav, and no footer. The home page carries its own small wordmark and way in, and a story's way in is its last step's Sign up.
- **Tabs:** pill tabs (real links), 44px tall with 0 18px padding and 6px gaps, muted inactive labels, an Info Tint pill on hover, and a Dollar Green pill with white text on the current tab. On the feed stage they are 44px pills with 0 16px padding with on-field-muted labels, and the current one is a Press Green pill with white text.

### Lists
Dense hairline rows with no cards inside cards. Gift and leader lists are bounded top and bottom by 1px lines, with 1px dividers between rows and 12px row padding. Titles are bold, amounts are right-aligned and tabular, and metadata wraps in muted 0.9375rem. Leaders use a three-column subgrid (rank, name, people), and your own row is filled with the Follow-through tint at 14px corners.

### The You Page
Your own profile is the home for your stuff (#132). The header is your name in Display with an outlined Settings button on the right, your region, the rewards panel, and your handles. Below, pill tabs (real links) switch between **Posts** and **Chipped in**. Posts starts with To confirm when gifts are waiting, then your posts as hairline rows: the bold title, "$X of $Y" on the right, the meter while open, and "Need · " plus one state mark that says what's next (Open until a date, Update due by a date, Update overdue as the disputed mark, Funded, In review, Closed), with small Post update, Edit, and Delete links. Chipped in lists your gifts with their state marks. Visitors see the header, handles, and public posts only, never what you gave. Settings (`/profile`) is a form page with a "← Your profile" link.

### Meter
The single progress device. It is a 4px pill track with an ink pill fill to the percentage. On a field it becomes a Field Track (20% ink) with a deep fill, 3px tall on the card. In forced-colors mode it is drawn in CanvasText.

### The Deck (signature)
One ask per screen, with a real link for each move. Dragging past 8px picks up the card. It follows the finger with a tilt of up to 4deg, and the neighboring ask's field is revealed underneath. After 24px of travel, the rail glyph for the target lights (Press Green disc, white glyph, scale 1.08); hover and focus light it the same way. A release past 30% of the card's width, or a flick faster than 0.5px/ms, throws it off the screen in 180ms with `cubic-bezier(0.4, 0, 1, 1)` and follows the link. Otherwise it settles back in 200ms with `cubic-bezier(0.16, 1, 0.3, 1)`. With no neighbor, the card gives at 25% resistance. With reduced motion, the card fades instead of moving (120ms). On desktop the rail glyphs are 60px circles with a 1.5px edge stroke and ink glyphs on the ground, filling ink with a ground-colored glyph on hover. Gestures: left = next, right = back, and down = show less arrives in #119.

### Photo State
A post may carry one poster photo (ADR 0015). On the feed card it fills the field edge to edge (`object-fit: cover`) and is itself masked into the field: transparent at 4%, solid from 18 to 30%, and gone by 58%, so the tabs, title, foot, and Chip in all sit on solid field. A wash of the field (85% to transparent by 22%) keeps the tabs on field at the very top. The title drops to sit just above the foot. On the post page the field header grows to `min(72vh, 600px)` (520px on desktop), with the photo solid to 30% and faded out by 62%. The ask's field stays underneath while the photo loads. A post with no photo is complete and never shows an empty frame.

### App Icon
The Home Screen icon (#185, #191, #200) is the deck in miniature, on Dollar Green: a Need Seafoam ticket tilted -4° over a Want Sage ticket tilted 9°, both with 56/1024 corners, and a dark-ink League Gothic **Y** at 560/1024, centered on the front ticket. The monogram replaced the stacked wordmark because "YEARNLY" on one line is too small to read at 60px, and iOS prints the name under the icon anyway. The maskable version scales the same art to 78%. It's rendered from `docs/brand/yearnly-icon.html` in the real font and exported to `app/static/icons/` (180, 192, 512, maskable 512, and a 32 favicon), and the 1024 master (`docs/brand/yearnly-icon-1024.png`) goes into the iOS app.

### The Home Page
The logged-out front door at `/` (#120) has no top bar (#205). It is one column on the jar-glass ground (22px from the top and 18px from the sides, plus the safe-area insets, with 16px gaps) holding a small wordmark, two speech bubbles, and the way in at the foot. Each bubble opens its own story, one step per server-rendered page, and the feed itself lives at `/feed`.
- **Wordmark:** "Yearnly" in League Gothic at 1.875rem in Dollar Green, as the page's h1 (read as "Yearnly: how it works").
- **Doors** (owner's Impeccable pick "Two Speech Bubbles", 2026-11-15): two linked bubbles in one green, Want Sage, in field ink with no scrim, 24px apart. "I want to help" stands 34px in from the right with its tail bottom-left, and "I need a hand" stands 34px in from the left with its tail bottom-right, so the second answers the first. A door carries one League Gothic line (clamp 2.75 to 4.25rem), a 1rem sentence (34ch max), and a bold "See how it works" with a 20px arrow that slides 4px on hover. There is deliberately no small label above the line: the craft floor bans eyebrows, so the line itself names the door. A door with photos is `clamp(220px, …, 360px)` tall on phones, and a door without photos is sized to its words. From 960px they sit side by side without offsets in a 1240px frame (28px gap, 32px padding, 380 to 580px tall), and a photo-less door drops to the foot of the row, so the ask answers lower. Focus is a field-ink 2px outline inset 6px.
- **Door photos** (owner's Impeccable pick "Tinted Mosaic", 2026-11-11): each door can carry a mosaic of real post photos across its top, clipped to the bubble's top corners. Photos are grayscale, contrast 0.7, brightness 1.25, multiplied into the door's own field color inside an isolated layer, so they read as the field rather than as pictures and dark ink can sit on them inside the smaller bubbles. Phones tile 3 across at 48% of the door's height; from 960px it is 3 by 2 at 62%. Seams are 3px. A fade to solid field (transparent at 18% to solid by 50% of the door on phones, 22% to 62% from 960px) runs before the words. A door shows six photos or none. The help door takes the six newest open asks with photos and the ask door the six newest funded asks, only from verified, unbanned, non-deleted accounts with no report ever on the account or any of its posts (`app/door_photos.py`). The ask door's sentence adds "These asks got there." only when it shows photos. The mosaic is `aria-hidden` with `alt=""` on every tile, and tiles 4 to 6 lazy-load, so phones never fetch the row they hide. From 960px the two doors share subgrid rows, so the headlines and links line up whatever length the sentences run.
- **Step photos** (owner's Impeccable pick "Photo Band", 2026-11-11): every story step carries three of its door's six photos (the help story the open asks, the ask story the funded ones) in a band across the top of the field, softened and multiplied into the field with 3px seams exactly like the doors. Steps alternate between photos 1 to 3 and 4 to 6, so neighboring steps never show the same ones and step 1 matches the tiles the phone door shows. On phones the band is 44% of the field, with a fade from transparent at 6% to solid field by 30%. From 960px the band is 52%, the fade runs 22% to 50%, and its columns are `1fr 1fr calc(400px + 40px + 28px)`, so the last seam falls in the gap left of the example column. The band is `aria-hidden` with `alt=""` on every photo, and a story shows no photos when its door has fewer than six. The doors and the steps share one macro, `app/templates/_mosaic.html`.
- **The way in:** at the foot of the column, a full-width 52px pill Sign up, then "Already have an account? Log in" centered in muted text with a bold ink link (420px max and centered from 960px). The "Yearnly never holds your money" promise line left the front door with the picked sketch (#205).
- **Stories:** `/how/help` and `/how/ask` (three steps each, #198), one step per page at `/how/<path>/<n>`, with no bar. The step is a column with 12px gutters (plus the safe-area insets) and a 22px gap. The field is a bubble in the story's color with its story's tail (help bottom-left, ask bottom-right), and it fills the screen: a row of 3px pill step bars (Field Track, deep through the current step), then the step line in League Gothic (clamp 2.75 to 4.25rem, 5.5rem at 960px and wider) with no label above it and no sentence under it (owner, 2026-11-14: "very simple, not as much wordage"), and one small example piece. At 960px the words and a 400px example column sit side by side (56px gap) inside the 1240px frame (24px gutters, 26px gap). The step nav at the foot of the field is Back, a tabular "n of N", and Next, all field-ink bold links with 20px arrows. Back from step 1 returns to the doors.
- **The other door:** waits below the field as a smaller bubble in its own color with its own tail (72px min, field ink and no scrim, a 1.75rem League Gothic line and "See how asking works" with the sliding arrow). On the last step it reads "Or see how …", and Next becomes a green pill Sign up to `/signup?from=<story>` (Go to the feed when logged in).
- **Sign-up page** (owner's Impeccable pick "Button Becomes the Form", 2026-11-12): `/signup` is the story's last step (owner, #208): like the front door it has no bar, no nav and no footer, and "Join in", its sentence, the form card and the Log in line all sit inside a speech bubble in the story's field color with that story's tail (sage with the help tail on plain `/signup`; 18px 18px 22px padding, 28px 32px 32px from 960px), hugging its content in a 480px column. Earlier it was a stage page on the ground for everyone, in a 480px column. "Join in" in League Gothic at Display Hero size, one muted sentence (40ch max), then the form in a white helper card with a 1.5px hairline edge, 22px corners with the 6px tail bottom-left, and 16px 18px padding, and below it "Already have an account? Log in" in muted text with a bold ink link. Arriving from a story (`?from=help` or `?from=ask`), a strip bubble in that story's field color with its story's pointed tail sits sticky at the foot, the bubble's 480px width, 18px above the screen foot on phones and sitting in place under the bubble from 960px: 56px min, a 20px back arrow and "Back to how helping works" (or asking), linking to that story's last step. The strip survives a rate-limited (429) submit. Any other `from` is ignored, and plain `/signup` has no strip.
- **Example pieces:** the real app components (the mini ask card, the Chip in panel, the To confirm row, the rewards meter, state marks) as white panels inside the field, under an "Example" tag: a 0.75rem 700 field-ink pill outlined in 1.5px field ink. Each piece mirrors the real app in its real state and shape, so the pay step shows the filled pay-app buttons a post without card gifts shows, and the thank-you step shows a confirmed gift with the recipient's thanks. Example buttons are inert (default cursor, no press). The mini ask card is a white ask bubble (28px with the 6px tail bottom-right, 360px max) with ink text, a 2.5rem League Gothic title, the meter, and a Marigold pill Chip in tab. It never takes a category color, so the only fields on a step are its own and the other door's strip (owner, 2026-11-12).
- **The arrival** (owner's Impeccable pick "The jar fills", 2026-11-14, #203): on a fresh open of `/` (the app launching, a typed URL, an outside link; never a same-site referrer or a back/forward visit), `how.js` sets `html.arrive` before the first paint. Each door's bubble fills up from its foot like a tip jar (`clip-path: inset(100% -24px -24px -24px)` to `inset(-24px)`, so the pointed tails are never clipped, 520ms `--ease-out`), help first and ask 110ms later. Each door's words rise 12px and fade in over 420ms from 300ms (ask from 410ms), and the way in fades in at 560ms. That's about 920ms in all. With reduced motion, the doors and the way in only fade in over 200ms. Without the class, everything is simply visible.
- **The move:** cross-document View Transitions, only under `prefers-reduced-motion: no-preference`. The door, the story field, and the docked strip share one name per story (`field-help`, `field-ask`), so the tapped door grows into the field and the other door shrinks into the strip in 460ms on `--ease-out`. The transition group clips its overflow (28px corners at 960px). It holds the story's own field color only when both pages carry that field (how.js adds `keep-help` / `keep-ask`), so a field with no partner just fades. The snapshots are unscaled and anchored left bottom, so a growing door never ghosts. The step content (`how-step`) wipes in from the right with `clip-path: inset(0 0 0 100%)` plus 32px over 420ms ease-out while the old step leaves left in 220ms ease-in. Going back reverses both directions. Opening a door or switching stories delays the incoming words 220ms so the field lands first. `how.js` is a blocking head script on the doors, story, and sign-up pages that sets these transition types on `pagereveal` (the doors count as step 0, sign-up from a story as step 99, so Back from it runs the back cut), and maps a 60px horizontal swipe (pointer, non-mouse) and the arrow keys to Back and Next.
- **The handoff:** from the last step to sign-up, the story's green Sign up pill (`join-card`) grows into the form card in 460ms on `--ease-out`, its group clipped at the pill radius. The old image is centered and fades out from 100 to 220ms, and the new image, anchored left top, fades in over the first 200ms. The step words leave and the page content cuts in (`how-step`), and the story field sinks into the strip (`field-help` / `field-ask`). Field groups stack at z-index 1, under `how-step` and `join-card` at 2, so the button and words always ride in front of the sinking field.
- **Fallback:** with reduced motion or no View Transition support, steps and the handoff are plain page navigations. Without JavaScript every step is still a link, and the stories are complete.

## Do's and Don'ts

### Do:
- **Do** keep the top bar and phone nav Dollar Green (#3a7558) with white type, the pages on the jar-glass ground, and the whole app light whatever the system setting.
- **Do** give each ask a Sage or Seafoam field with field-ink type and no scrim, and check that any new category color holds dark ink at 4.5:1 or better.
- **Do** shape asks as 28px bubbles with the 6px tail corner bottom-right, and helper panels as 22px bubbles with the 6px tail corner bottom-left.
- **Do** make every button, tab, and Chip in tab a pill, and keep inputs, flashes, and notices at 14px.
- **Do** fade every photo into the field's own color so the words, tabs, and Chip in sit on solid field.
- **Do** set titles in League Gothic uppercase and everything else in Public Sans, with tabular numerals for money and counts.
- **Do** use the green filled button for the screen's main action, Marigold only for Chip in, and outline everything else.
- **Do** show progress only with the thin pill meter, and lists only as hairline rows.
- **Do** use Lucide line icons at a 2px stroke from the `_icons.html` sprite, always with a visible text label.
- **Do** back every gesture with a labeled button and a real link, so the feed works without JavaScript and at 360px with no horizontal scroll.
- **Do** say "gift" and "chip in" in interface copy.
- **Do** label every demo piece of the app "Example" with the outlined pill tag, and make it mirror the real component, its shape, and its real state exactly.

### Don't:
- **Don't** use black or a neutral gray-black anywhere, or add a dark mode.
- **Don't** put white text or a dark scrim on a Sage or Seafoam field.
- **Don't** use Marigold for anything but Chip in, or tomato for anything but errors, disputed gifts, and destructive actions.
- **Don't** add box or drop shadows, glass, glow, or gradients other than the fades into the field's own color.
- **Don't** give a bubble more than one tight corner, point an ask's tail left or a helper's right, or hang a pointed tail on anything but the home doors, the story fields, and the docked strips.
- **Don't** turn a gift's state into a pill or a filled badge. Use a shape and a word.
- **Don't** add a second progress style for money or goals (rings, segmented bars, or percentages as hero numbers). The segmented step bars on the How stories mark place in a story, never progress toward a goal.
- **Don't** nest cards in panels or lay asks out as a card grid or vertical-scroll feed.
- **Don't** put a top bar back on the logged-out front door.
- **Don't** say "donation" or "charity" anywhere in the interface.
- **Don't** invent stats, counts, testimonials, or quotes on marketing surfaces. The proof is the real app pieces, labeled Example.
