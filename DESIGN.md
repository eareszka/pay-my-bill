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

Away from the stage, the working pages (Gifts, Leaders, profile, forms, admin, legal) are quiet and dense. They follow the system color scheme: cool paper and white panels in light, near-black panels in dark. They share the same two typefaces, the same inverse filled button, and the same hairline language. Lists are hairline rows, progress is a single hairline meter, and states are a small shape plus a word. There are no shadows, glass, or glow, and no gradient except the scrim that keeps white text legible at the foot of a color field.

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

On phones, the top bar is 52px tall and the nav is a fixed 64px bar at the bottom (plus the safe-area inset) with five icon-over-label items, the signed-in username in place of "You". The feed stage fills the height between the two bars (minimum 520px). Inside it, the All, Needs, and Wants tabs are centered at the top, the title sits mid-screen, and the foot holds meta, a three-line story, amounts, and the meter. The rail (Back, Next, and the count) sits at the right edge, and the full-width Chip in tab is at the bottom.

At 960px the nav moves into a 60px top bar as icon-beside-label items, centered within 1120px. The feed becomes one wide card, centered within about 1240px: the ask (up to 660px wide, `min(620px, 100dvh - 230px)` tall, 460px minimum) joined to a 400px Chip in panel on surface, with 18px outer corners. The tabs sit centered above it. Back and Next are 60px outlined circles in 88px gutters outside the card, and the count with an "← → to move" hint sits centered below. The title rests just above who and where, as on the post hero. The on-card Chip in tab is hidden because the panel replaces it. Dragging still works but nothing depends on it, and a click or arrow key plays the same 180ms slide. The post page becomes a fluid story column beside a 400px side panel. Below 380px, the card's right padding tightens to 76px so the title clears the rail. The body clips horizontal overflow, so a thrown card never adds a sideways scroll.

## Elevation & Depth

The system is flat. Depth comes from tonal layering (void, then the color field, then white controls) and, during a drag, from the real neighboring ask sitting underneath the one in your hand. The only soft shadow is a legibility aid on the rail glyphs over bright fields, and it disappears when a glyph lights.

### Shadow Vocabulary
- **Glyph lift** (`filter: drop-shadow(0 1px 2px rgb(0 0 0 / 0.45))`): only on unlit rail glyphs over a color field.

### Named Rules
**The Scrim Only Rule.** The one gradient is the bottom scrim on a color field (transparent to 40% black over the lower half on cards, and over the lower 60% on the post hero). No other gradients, glass, glow, or box shadows.

## Shapes

Corners are gentle and scale with the size of the object: 2px on the meter, 6px on badges, 8px on buttons, inputs, flashes, and desktop nav items, 12px on the Chip in tab, 14px on panels, and 18px on the desktop stage and post hero. On phones the stage and hero bleed edge to edge with no corners. Rail glyphs sit in 52px circles that fill white when engaged. Borders are 1px hairlines for structure, 1.5px for control strokes, and 2px for invalid fields and tab underlines.

## Components

### Buttons
Plain and confident. There is one inverse fill, and everything else is drawn in outline.
- **Shape:** gently rounded (8px), at least 46px tall, padding 10px 18px, Public Sans 700.
- **Primary:** ink fill with white text on light pages, and white fill with void text on dark pages and the stage. Hover shifts the fill one step (action-hover). Pressing scales it to 0.98.
- **Secondary:** transparent with a 1.5px edge stroke and ink text. Hover darkens the stroke to ink.
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
- **Phone:** a fixed void bar at the bottom with Lucide 24px icons over 0.75rem 700 labels in fog gray. The current page turns white and its icon stroke thickens to 2.5. A white count badge marks gifts waiting to be confirmed.
- **Desktop (960px and wider):** the same items, inline in the top bar with 20px icons and 0.9375rem labels. The current page gets a slate fill with 8px corners.
- **Tabs:** text tabs with a 2px underline on the current tab (white on the stage, ink elsewhere) and muted inactive tabs over a hairline.

### Lists
Dense hairline rows with no cards inside cards. Gift and leader lists are bounded top and bottom by 1px lines, with 1px dividers between rows and 12px row padding. Titles are bold, amounts are right-aligned and tabular, and metadata wraps in muted 0.9375rem. Leaders use a three-column subgrid (rank, name, people).

### Meter
The single progress device. It is a 4px hairline track with 2px corners and an ink fill to the percentage. On a color field it becomes a 30% white track with a white fill, and 3px tall on the card. In forced-colors mode it is drawn in CanvasText.

### The Deck (signature)
One ask per screen, with a real link for each move. Dragging past 8px picks up the card. It follows the finger with a tilt of up to 4deg, and the neighboring ask's field is revealed underneath. After 24px of travel, the rail glyph for the target lights (white disc, void glyph, scale 1.08). A release past 30% of the card's width, or a flick faster than 0.5px/ms, throws it off the screen in 180ms with `cubic-bezier(0.4, 0, 1, 1)` and follows the link. Otherwise it settles back in 200ms with `cubic-bezier(0.16, 1, 0.3, 1)`. With no neighbor, the card gives at 25% resistance. With reduced motion, the card fades instead of moving (120ms). Gestures: left = next, right = back, and down = show less arrives in #119.

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

### Don't:
- **Don't** use tomato for anything but errors, disputed gifts, and destructive actions.
- **Don't** add box shadows, glass, glow, or gradients other than the field scrim.
- **Don't** put colored text or colored controls on a color field. It's white or nothing.
- **Don't** turn state into pills or badges with fills. Use a shape and a word.
- **Don't** add a second progress style (rings, segmented bars, or percentages as hero numbers).
- **Don't** nest cards in panels or lay asks out as a card grid or vertical-scroll feed.
- **Don't** say "donation" or "charity" anywhere in the interface.
