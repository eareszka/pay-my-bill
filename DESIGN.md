---
name: Pay My Bill
description: A community bulletin board for everyday wants and needs. One ticket up close, one green tab to chip in.
colors:
  action: "#1f5a3d"
  action-hover: "#17452f"
  on-action: "#ffffff"
  mark: "#1f5a3d"
  mark-empty: "#e4ddd2"
  link-surface: "#1f5a3d"
  link-on-ground: "#231a12"
  want: "#cfe3f5"
  tomato: "#b8452c"
  tomato-hover: "#9d3a24"
  tomato-text: "#9d3a24"
  on-tomato: "#ffffff"
  ground: "#c49a6c"
  bar: "#4a2f1b"
  on-bar: "#ffffff"
  surface: "#ffffff"
  ink: "#231a12"
  ink-on-light: "#231a12"
  on-ground: "#231a12"
  muted-surface: "#54463a"
  muted-on-ground: "#2f2114"
  line: "#d8ccbd"
  rule: "#4a2f1b"
  stack-1: "#cfe3f5"
  stack-2: "#efe6d8"
  tint-info: "#efe6d8"
  tint-good: "#d9eadf"
  tint-bad: "#f7dfd8"
  action-dark: "#2c7a53"
  action-hover-dark: "#256a48"
  mark-dark: "#62c390"
  mark-empty-dark: "#453628"
  link-surface-dark: "#86d8ac"
  link-on-ground-dark: "#f3ebdf"
  want-dark: "#1b2f3f"
  tomato-dark: "#f08a72"
  tomato-hover-dark: "#f5a28e"
  tomato-text-dark: "#f08a72"
  on-tomato-dark: "#231a12"
  ground-dark: "#33261a"
  bar-dark: "#1a110a"
  surface-dark: "#1e1711"
  ink-dark: "#f3ebdf"
  on-ground-dark: "#f3ebdf"
  muted-surface-dark: "#c4b5a2"
  muted-on-ground-dark: "#dccdb9"
  line-dark: "#453628"
  rule-dark: "#dccdb9"
  stack-1-dark: "#4a6a85"
  stack-2-dark: "#6b5540"
  tint-info-dark: "#33291e"
  tint-good-dark: "#1d3d2c"
  tint-bad-dark: "#43241c"
typography:
  display:
    fontFamily: "Bitter, Georgia, serif"
    fontSize: "2.625rem"
    fontWeight: 800
    lineHeight: 1.15
  post-title:
    fontFamily: "Bitter, Georgia, serif"
    fontSize: "2.375rem"
    fontWeight: 800
    lineHeight: 1.15
  ticket-title:
    fontFamily: "Bitter, Georgia, serif"
    fontSize: "2.125rem"
    fontWeight: 800
    lineHeight: 1.15
  headline:
    fontFamily: "Bitter, Georgia, serif"
    fontSize: "1.75rem"
    fontWeight: 800
    lineHeight: 1.15
  title:
    fontFamily: "Bitter, Georgia, serif"
    fontSize: "1.25rem"
    fontWeight: 800
    lineHeight: 1.15
  brand:
    fontFamily: "Bitter, Georgia, serif"
    fontSize: "1.125rem"
    fontWeight: 800
    lineHeight: 1.15
  list-title:
    fontFamily: "Bitter, Georgia, serif"
    fontSize: "1.0625rem"
    fontWeight: 800
    lineHeight: 1.2
  amount-panel:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.875rem"
    fontWeight: 700
    lineHeight: 1.5
  gift-amount:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.625rem"
    fontWeight: 700
    lineHeight: 1.2
  amount-ticket:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.5
  story:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.5
  tear-tab:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 700
    lineHeight: 1.5
  amount:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 700
    lineHeight: 1.5
  story-phone:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 700
    lineHeight: 1.5
  hint:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.5
  fine:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  count:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 700
    lineHeight: 1.67
rounded:
  paper: "0px"
  disputed: "2px"
  control: "3px"
  tag: "4px"
  mark: "5px"
  count: "10px"
spacing:
  hairline: "4px"
  tight: "8px"
  stack: "12px"
  panel: "14px"
  page: "16px"
  split: "24px"
  ticket-wide: "28px"
  section: "32px"
components:
  button-primary:
    backgroundColor: "{colors.action}"
    textColor: "{colors.on-action}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "{colors.action-hover}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
    height: "44px"
  button-danger:
    backgroundColor: "{colors.tomato}"
    textColor: "{colors.on-tomato}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
    height: "44px"
  button-danger-hover:
    backgroundColor: "{colors.tomato-hover}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
    height: "46px"
  ticket:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.paper}"
    padding: "16px"
  ticket-want:
    backgroundColor: "{colors.want}"
    textColor: "{colors.ink}"
    rounded: "{rounded.paper}"
    padding: "16px"
  tear-tab:
    backgroundColor: "{colors.action}"
    textColor: "{colors.on-action}"
    typography: "{typography.tear-tab}"
    rounded: "{rounded.paper}"
    padding: "15px"
  tear-tab-hover:
    backgroundColor: "{colors.action-hover}"
  chip-in-panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.paper}"
    padding: "14px"
    width: "416px"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.paper}"
    padding: "14px"
  topbar:
    backgroundColor: "{colors.bar}"
    textColor: "{colors.on-bar}"
  mark-on:
    backgroundColor: "{colors.mark}"
    rounded: "{rounded.mark}"
    height: "13px"
  mark-empty:
    backgroundColor: "{colors.mark-empty}"
    rounded: "{rounded.mark}"
    height: "13px"
  flash-info:
    backgroundColor: "{colors.tint-info}"
    textColor: "{colors.ink}"
    rounded: "{rounded.paper}"
    padding: "10px 12px"
  flash-success:
    backgroundColor: "{colors.tint-good}"
    textColor: "{colors.ink}"
    rounded: "{rounded.paper}"
    padding: "10px 12px"
  flash-error:
    backgroundColor: "{colors.tint-bad}"
    textColor: "{colors.ink}"
    rounded: "{rounded.paper}"
    padding: "10px 12px"
---

# Design System: Pay My Bill

## Overview

**Creative North Star: "The Community Board at the Door"**

Pay My Bill is a community bulletin board, and the owner chose that world. Each post is a plain square ticket on cork: a big slab title, a short story, and how much has come in so far. A visitor sees one person up close, then chips in or moves on to the next ticket. The ticket reads simple and trustworthy, with its personality coming from the heavy title, the warm cork, and the green tab you tear off to help.

The materials are stated, not imitated. Cork is one flat tan and the wood bar is one flat brown, with no grain, texture, or image behind either. Paper is the only thing that lifts, on one soft shadow. There are no thumbtacks. Phones get One Ticket at a Time, with a green tear-off Chip in tab. Screens 960px and wider get Give Right Here, with the ticket and the Chip in panel side by side in a centered layout. The owner tried a full-browser layout and rejected it, so a full-width layout is not wanted.

The owner's brief rules out five looks: a sad charity page, a bank or finance app, a game or casino, a generic startup, and a typical scroll app. Light and dark themes follow the system setting and keep the same roles: dark is the same board with the lights down, not a different world.

**Key Characteristics:**
- One ticket at a time, with the rest of the stack peeking out behind it, instead of a grid or an endless list.
- Flat cork and a flat wood bar, with no faked material and no thumbtacks.
- Square paper tickets on one soft shadow: white for needs, light blue for wants.
- Green for primary actions, links, and progress marks. Tomato for errors and destructive actions.
- Two typefaces: Bitter extra-bold for titles, Public Sans for everything else, including all money.

## Colors

A warm brown board with paper on top, one working green, and one warm colour for trouble.

### Primary
- **Leaf Green** (#1f5a3d light, #2c7a53 dark; hover #17452f light, #256a48 dark): Primary buttons and the tear-off Chip in tab, always with white text (8.11:1 light, 5.23:1 dark).
- **Progress Green** (#1f5a3d light, #62c390 dark): Filled progress marks and the confirmed-gift dot, plus the pressed-reaction border and the text caret. It lightens in dark mode so it stays visible on dark paper, and form choices tint with it there.
- **Paper Link Green** (#1f5a3d light, #86d8ac dark): Underlined links on paper. Links on cork use Cork Link Ink instead, because leaf green only reaches 3.16:1 on cork.

### Secondary
- **Want Blue** (#cfe3f5 light, #1b2f3f dark): The paper of a want, on the ticket and the post page.

### Tertiary
- **Tomato** (#b8452c light, #f08a72 dark; hover #9d3a24 light, #f5a28e dark): Destructive buttons, invalid-field borders, and the disputed mark. Button text is white in light mode and dark ink in dark mode.
- **Tomato Text** (#9d3a24 light, #f08a72 dark): Words that report an error or a disputed gift. It holds at least 5.2:1 on white paper, want blue, and the bad tint.

### Neutral
- **Cork** (#c49a6c light, #33261a dark): The page behind everything. A flat fill, and a real reading surface: ink holds 6.67:1 in light and 12.39:1 in dark.
- **Wood** (#4a2f1b light, #1a110a dark): The top bar, the browser theme colour, and text selection. White text sits on it in both themes.
- **Paper** (#ffffff light, #1e1711 dark): Need tickets, post pages, panels, forms, form fields, and secondary buttons.
- **Ink** (#231a12 light, #f3ebdf dark): Text on paper, plus the shared focus ring. Cork text uses the same values through its own on-cork token, and Ink on Light (#231a12) stays dark in both themes for the white count capsule in the bar.
- **Muted on Paper** (#54463a light, #c4b5a2 dark): Hints, metadata, and field borders on paper and tints.
- **Muted on Cork** (#2f2114 light, #dccdb9 dark): Inactive tabs and hints that sit directly on cork.
- **Cork Link Ink** (#231a12 light, #f3ebdf dark): Underlined links that sit directly on cork.
- **Paper Line** (#d8ccbd light, #453628 dark): Dividers inside a sheet, such as list rows and the rule between a post and its panels.
- **Board Rule** (#4a2f1b light, #dccdb9 dark): The tab rules and the rule above the danger zone, both on cork.
- **Empty Mark** (#e4ddd2 light, #453628 dark): Unfilled progress marks, outlined with a faint inner ring so they still show on want blue.
- **Stack Edges** (#cfe3f5 and #efe6d8 light, #4a6a85 and #6b5540 dark): The two sheet edges peeking out above a ticket when more tickets wait. They show only that more tickets exist, not what kind. In light mode the first matches Want Blue, so a blue edge can show on the Needs tab; that overlap is open drift, not a precedent.
- **Info Tint** (#efe6d8 light, #33291e dark): Neutral flashes and notices.
- **Good Tint** (#d9eadf light, #1d3d2c dark): Success flashes, earned-badge tags, your own leaderboard row, and pressed reactions.
- **Bad Tint** (#f7dfd8 light, #43241c dark): Error flashes and notices, with ink text.

### Named Rules

**The Working Green Rule.** Green is used for primary actions, links, and progress marks, as the owner decided. Green never colours the bar, the ground, the paper, or a decoration.

**The One Decision Rule.** A panel offers one primary green decision at a time. A set of equal pay-app choices counts as one decision. Everything else on that panel is secondary.

**The Tomato Rule.** Tomato means an error or a destructive action. It never decorates and never signals urgency on its own.

**The Flat Materials Rule.** Cork and wood are flat fills. No grain, texture, gradient, or image may fake either material, in either theme.

## Typography

**Display Font:** Bitter 800 (with Georgia, serif)
**Body Font:** Public Sans 400 and 700 (with system-ui, -apple-system, Segoe UI, sans-serif)

**Character:** A heavy slab that could be hand-lettered across the top of a notice, beside a plain public-signage sans whose unslashed zeros read cleanly on money. All three font files are self-hosted, with `font-display: swap`.

### Hierarchy
- **Display** (800, 2.625rem, 1.15): The ticket title and the post title at 960px and wider.
- **Post Title** (800, 2.375rem at most, 1.15): The post title below 960px, fluid from 1.75rem at 8vw.
- **Ticket Title** (800, 2.125rem at most, 1.15): The ticket title below 960px, fluid from 1.75rem at 8vw.
- **Headline** (800, 1.75rem, 1.15): Page titles such as Gifts, Leaders, and Log in.
- **Title** (800, 1.25rem, 1.15): Panel and section titles, the level on a profile, and the "did you send it" question. A nested section title steps down to 1.0625rem.
- **Brand** (800, 1.125rem, 1.15): The name in the top bar and form-group legends.
- **List Title** (800, 1.0625rem, 1.2): Post titles in the gift list.
- **Panel Amount** (700, 1.875rem, 1.5): The raised figure at the top of the Chip in panel on the board, beside the goal in regular weight.
- **Gift Amount** (700, 1.625rem, 1.2): The amount on a gift waiting to be confirmed.
- **Ticket Amount** (700, 1.5rem, 1.5): The raised figure on a phone ticket, beside the goal at 1.0625rem.
- **Story** (400, 1.125rem, 1.5): The short story on a ticket at 960px and wider.
- **Tear Tab** (700, 1.125rem, 1.5): The Chip in label on the tear-off tab.
- **Amount** (700, 1.125rem, 1.5): The raised figure on the post page.
- **Phone Story** (400, 1.0625rem, 1.5): The short story on a ticket below 960px.
- **Body** (400, 1rem, 1.5): All running text. A post's story stops at 70ch.
- **Label** (700, 1rem, 1.5): Field labels, buttons, tabs, and the ticket count.
- **Hint** (400, 0.9375rem, 1.5): Guidance on cork and inside panels, and who and where on the post page. Top-bar links use this size at 700.
- **Fine** (400, 0.875rem, 1.5): Who and where on a ticket, field help and errors, state marks at 700, and badge tags at 700.
- **Count** (700, 0.75rem, 20px line): The number in the top-bar capsule.

Titles use balanced wrapping, and paragraphs and list items use pretty wrapping. Long usernames are cut with an ellipsis in the top bar. Everywhere else, long text wraps at any character so nothing overflows.

### Named Rules

**The Two Voices Rule.** Bitter 800 is for titles only. Everything else, and all money, is Public Sans at 400 or 700. No other weights are loaded, so none may be requested.

**The Size Carries Rank Rule.** Rank comes from size and the shift of typeface. There is no uppercase, no letterspacing, and no small label above a heading anywhere in the system.

**The Money Lines Up Rule.** Figures in lists and columns are right-aligned with tabular numerals, tight against what they belong to.

## Layout

The board and the post page use the only two-part layout, and it changes at 960px. Every other page (Gifts, Leaders, profile, forms, log in, rules, and errors) stays one centered column of 640px at most, with 16px page padding, at every screen size. The wood bar's colour runs edge to edge. Its contents line up to 608px below 960px and 1120px from 960px up.

**Below 960px: One Ticket at a Time.** The owner's choice, after a grid of posts was rejected as cluttered and too much like a scroll site. One centered ticket, 480px at most, sits under the All, Needs, and Wants tabs. It fills the screen down to the Next ticket row, up to 520px tall, with the story at the top and the amount pushed to the bottom above the Chip in tab. The post page is one 608px sheet with its panels below the story.

**960px and wider: Give Right Here.** The owner's choice, so people can give without leaving. The layout is centered, 1152px at most with 16px padding (`.container-wide`), leaving 1120px of content. The ticket takes the left side with who and where, and a fixed 416px Chip in panel stands right beside it with a 24px gap, at matching height. The ticket has a 520px minimum height and 28px padding, and the count and Next ticket sit below both. The post page uses the same split inside one sheet whenever it has a panel to show, with a 28px gap and a 2px paper line between the two sides. With no panel to show, the post stays one sheet at full 1120px, its story still stopped at 70ch.

Spacing steps are 4px within a label and control, 8px between related actions, 12px between stacked pieces, 14px inside panels and between form fields, 16px on ticket bodies and at the page edge, 24px above the danger zone and across the board's split, and 32px between sections on Gifts. Forms are full-width single columns, and paired actions sit side by side and wrap.

Every page must work at 360px without horizontal scroll. Below 400px the top bar tightens to 12px padding and its links drop to 0.875rem. Pay-app buttons share a row and wrap at a 96px minimum.

### Named Rules

**The One Ticket Rule.** The board shows one ticket at a time, on every screen size. It never becomes a grid, a rack, or an endless list.

**The Give Right Here Rule.** At 960px and wider, the ticket and the Chip in panel stand side by side. On phones, the same step is one tap away through the tear-off tab.

**The Centered Board Rule.** A full-width layout is not wanted: the owner tried a full-browser layout and rejected it. Page content stays inside the centered 1152px container at any screen size, and the extra width is plain cork.

## Elevation & Depth

Paper lifts and nothing else does. Every sheet on the board (tickets, stack edges, post pages, panels, forms, gift cards, lists, flashes, and notices) casts the same soft shadow onto the cork, and the wood bar casts none. Inside a sheet, depth stops: panels and notices within a post or the Chip in form lose their shadow and become part of the same page, divided by a 2px paper line where they need one. There is no hover lift.

### Shadow Vocabulary
- **Paper shadow** (`box-shadow: 0 2px 5px rgba(50, 30, 10, 0.35)` light, `0 2px 5px rgba(0, 0, 0, 0.5)` dark): Every sheet on the cork. In dark mode it does most of the work of separating paper from the board.
- **Pressed reaction** (`box-shadow: inset 0 0 0 1px var(--mark)`): Doubles the border weight on a reaction that is on.
- **Empty mark ring** (`box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--muted) 35%, transparent)`): Outlines an unfilled progress mark.

### Named Rules

**The One Sheet of Paper Rule.** All paper uses the one soft shadow, at rest. A sheet on a sheet gets no second shadow, and no shadow gets harder, offset, or larger to win attention.

## Shapes

Paper is cut square, with no radius on tickets, post pages, panels, forms, gift cards, or flashes. Controls are only slightly softened: 3px on buttons, fields, and the skip link. Small pieces keep their own forms: 5px on progress marks, 4px on earned-badge tags, and a 10px capsule on the top-bar count. Round dots mark gift states, and the disputed mark alone is a 2px-cornered square, so it differs in shape as well as colour. Borders are 1.5px on controls, 2px under tabs and for rules, and 1px between list rows. The one dashed line in the system is the 2px white tear edge on the Chip in tab.

### Named Rules

**The Square Paper Rule.** Anything that reads as a sheet of paper has square corners. Pill buttons and large rounded cards do not belong on this board.

**The No Thumbtacks Rule.** Tickets are not pinned, taped, tilted, or otherwise dressed up, and the owner has ruled out thumbtacks. Paper, a shadow, and the tear-off tab are all the board needs.

## Components

### Ticket
The signature container, and the only post on the board at one time. A ticket with no photo is complete.
- **Structure:** A Bitter title, a short story cut to 140 characters, and the amount. Who and where appear on the ticket at 960px and wider, and on the post page at every width. The kind shows in the paper colour, white for a need and Want Blue for a want, and at 960px and wider the who-and-where line also says it in words.
- **Interaction:** The whole ticket opens the post, through a link stretched over the title. The poster's name and the Chip in tab stay their own targets above that layer. Hover underlines the title. Focus draws a 3px ink ring just inside the ticket edge.
- **Stack:** When more than one ticket is waiting, two sheet edges peek out above the ticket, 12px and 6px narrower on each side and sharing the paper shadow. A lone ticket has no stack.
- **Photo state (planned, not built):** Optional poster photos come in a later story. No tokens or styles exist for them yet.

### Tear-Off Chip In Tab
The phone's one action on a ticket: a full-width leaf-green tab along the ticket's bottom edge, with white 700 text and a 2px dashed white tear line on top. It has square corners and 15px padding, and hover deepens the green. Its focus ring is white and inset, so it stays on the tab. It opens the post page at the Chip in panel. It appears below 960px only, and is left off when the viewer is the poster or the poster has no payment app.

### Chip In Panel
The giving step: the amount field, the pay-app buttons, then a separate "Sent it?" step. On the board at 960px and wider it is its own white sheet beside the ticket, 416px wide and matching the ticket's height, with the raised amount at the top. On the post page it is part of the sheet, taking on the sheet's colour. Pay-app buttons are the panel's one primary decision and "I sent it" is secondary, until the page asks whether you sent it, when that button becomes the primary.

### Ten-Mark Row
Ten equal marks that fill left to right with 4px gaps, always with an amount or XP figure beside them. Any progress shows at least one mark, and the tenth fills only at 100%.
- **Post page:** 13px tall. Filled marks grow in once on load, 280ms each with a 45ms stagger. Reduced motion shows them filled at once.
- **Profile:** 9px tall with no motion, for progress toward the next level.
- **Board ticket:** No row. The amount in words does the work, so the row keeps its moment on the post page.

### Buttons
Plain and sure of themselves.
- **Shape:** Slightly softened corners (3px), at least 44px tall, with 10px 18px padding and a 1.5px border.
- **Primary:** Leaf green with white text at 700.
- **Secondary:** Paper fill, ink text, muted border. Used for Next ticket, Back, Cancel, "I sent it", "Didn't get it", and the entry points to close or delete. The hover darkens only the border.
- **Danger:** Tomato fill. It appears only on the confirming step of a delete or dispute; the step before it is secondary.
- **Hover / Focus:** Fill and border colours shift over 120ms ease-out, and a press drops the button 1px. Focus is the shared 3px ink ring at 2px offset.
- **Disabled:** 55% opacity with a not-allowed cursor.

### Reactions
A secondary button with 8px 14px padding and tabular counts. When on, it takes the good tint and a progress-green double border. Visitors who cannot react see the counts as plain muted text instead of a disabled button.

### Cards / Containers
- **Corner Style:** Square.
- **Background:** Paper on cork, or Want Blue for a want.
- **Shadow Strategy:** The paper shadow; none for a sheet inside a sheet.
- **Border:** None. In forced-colors mode each sheet gains a 1px border.
- **Internal Padding:** 16px on ticket bodies and full-page forms, 14px on panels and gift cards, and 12px 14px on list rows, which are divided by a 1px paper line.

### Inputs / Fields
- **Style:** Paper fill, 1.5px muted border, 3px corners, 10px 12px padding, at least 46px tall (textareas 120px). The label sits above in 700 and the hint below in muted.
- **Focus:** The 3px ink ring at no offset, and the border turns ink.
- **Error:** A 2px tomato border, with the message below in tomato text at 700, linked to the field.
- **Choices:** 20px radios and checkboxes tinted by the theme accent, in 32px rows.

### Navigation
- **Top bar:** Flat wood band. Brand at left in Bitter; links at right in 700 and 0.9375rem, with 12px vertical padding for reach. Hover adds a 2px underline. A count of waiting gifts is a white capsule with dark text. Focus turns the ring white.
- **Tabs:** 700 muted text on cork over a 2px board rule. The current tab goes full ink with a 4px underline that sits on the rule. A second tab row stacks directly under the first where a page has two filters.
- **Ticket row:** Under the ticket, on cork: a secondary Back after the first ticket, the "2 of 8" count in 700, and a secondary Next ticket pushed to the right, which returns to the first ticket from the last.

### State Mark
One device for every gift state: a small mark before a 0.875rem, 700 label. It carries no pill or background.
- **Waiting:** Hollow muted ring.
- **Confirmed:** Filled progress-green dot.
- **Not received:** Tomato square with tomato text.
- **Expired:** Empty-mark dot with muted text.

### Flashes and Notices
Full-width tinted sheets above the content with ink text, 10px 12px padding, and square corners: info, success, or error by tint and words. Error flashes are announced as alerts.

### Motion

The feed moves like a pile of mail being dealt, and nothing else on the site gets a similar effect.

- **Drag:** the ticket follows the pointer and tilts up to 6°, with a blank sheet underneath.
- **Swipe left or Next ticket:** the ticket flies off left in 200ms, and the next one rises from the pile in 250ms.
- **Swipe right or Back:** the ticket flies off right in 200ms, and the previous one returns from the left in 300ms.
- **Let go early:** the ticket settles back in 250ms. With nowhere to go, it gives a quarter of the drag and springs back.
- **Reduced motion:** no flight or tilt, only a 120ms fade.

Swiping only moves through the pile. It never gives, passes on, or hides a post.

## Do's and Don'ts

### Do:
- **Do** show one ticket at a time on the board, with the stack peeking out when more wait.
- **Do** keep the tear-off Chip in tab on phones and put the ticket and Chip in panel side by side from 960px.
- **Do** keep the board and post page inside the centered 1152px container, and leave the other pages in the 640px column.
- **Do** use green for primary actions, links on paper, and progress marks, and switch to Cork Link Ink for links on cork.
- **Do** give cork text the on-cork muted and link tokens, and paper text the on-paper ones.
- **Do** treat a ticket with no photo as finished.
- **Do** show progress with the ten-mark row and state the same fact in words beside it.
- **Do** put one primary green decision in a panel, and make any delete or dispute a two-step move ending in tomato.
- **Do** keep money in Public Sans, with tabular numerals wherever figures are listed in a column.
- **Do** check every new surface in both themes and at 360px wide.

### Don't:
- **Don't** build a full-width layout. The owner tried a full-browser layout and rejected it.
- **Don't** put posts back in a grid, a rack, or a scrolling list on the board.
- **Don't** add thumbtacks, pins, tape, tilted tickets, or plant art.
- **Don't** fake cork or wood with grain, texture, gradients, or images.
- **Don't** use green as decoration, or on the bar, the ground, or a sheet of paper.
- **Don't** use tomato for emphasis, urgency, or decoration.
- **Don't** drift toward a sad charity page, a bank or finance app, a game or casino, a generic startup, or a typical scroll app.
- **Don't** add hard offset shadows, hover lifts, or a second shadow on a sheet inside a sheet.
- **Don't** add pill buttons, large rounded cards, or small uppercase labels above headings.
- **Don't** load another weight or typeface, or set money in Bitter.
- **Don't** render an empty image frame for a post with no photo, or treat the planned photo state as shipped.
- **Don't** extend the reaction emoji into a general icon set. They are the content of those two reactions and nothing more.
