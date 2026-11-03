---
name: Pay My Bill
description: A garden-aisle seed packet for everyday wants and needs. Plain facts, a growing row, one action.
colors:
  leaf: "#1f5a3d"
  mark: "#1f5a3d"
  mark-empty: "#d2e0d7"
  link: "#1f5a3d"
  teal: "#0f5e6e"
  on-band: "#ffffff"
  action: "#f4b223"
  action-hover: "#e5a412"
  on-action: "#17231c"
  tomato: "#b8452c"
  tomato-hover: "#9d3a24"
  on-tomato: "#ffffff"
  ground: "#e6f0ea"
  surface: "#ffffff"
  ink: "#17231c"
  muted: "#46574e"
  line: "#c3d4ca"
  tint-info: "#d6e7dd"
  tint-good: "#cfe6d8"
  tint-bad: "#f7dfd8"
  ground-dark: "#0f1a14"
  surface-dark: "#18251e"
  ink-dark: "#edf4ef"
  muted-dark: "#a9bcb0"
  line-dark: "#304238"
  link-dark: "#86d8ac"
  action-hover-dark: "#ffc53d"
  tomato-dark: "#f08a72"
  tomato-hover-dark: "#f5a28e"
  on-tomato-dark: "#17231c"
  mark-dark: "#62c390"
  mark-empty-dark: "#304238"
  tint-info-dark: "#20352a"
  tint-good-dark: "#1d3d2c"
  tint-bad-dark: "#43241c"
typography:
  display:
    fontFamily: "Bitter, Georgia, serif"
    fontSize: "2.375rem"
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
  packet-title:
    fontFamily: "Bitter, Georgia, serif"
    fontSize: "1.125rem"
    fontWeight: 800
    lineHeight: 1.15
  list-title:
    fontFamily: "Bitter, Georgia, serif"
    fontSize: "1.0625rem"
    fontWeight: 800
    lineHeight: 1.2
  gift-amount:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.625rem"
    fontWeight: 700
    lineHeight: 1.2
  amount:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "1.1875rem"
    fontWeight: 700
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
rounded:
  panel: "6px"
  mark: "5px"
  tag: "4px"
  count: "10px"
spacing:
  hairline: "4px"
  tight: "8px"
  rack: "10px"
  stack: "12px"
  panel: "14px"
  page: "16px"
  section: "32px"
components:
  button-primary:
    backgroundColor: "{colors.action}"
    textColor: "{colors.on-action}"
    typography: "{typography.label}"
    rounded: "{rounded.panel}"
    padding: "10px 18px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "{colors.action-hover}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.panel}"
    padding: "10px 18px"
    height: "44px"
  button-danger:
    backgroundColor: "{colors.tomato}"
    textColor: "{colors.on-tomato}"
    typography: "{typography.label}"
    rounded: "{rounded.panel}"
    padding: "10px 18px"
    height: "44px"
  button-danger-hover:
    backgroundColor: "{colors.tomato-hover}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.panel}"
    padding: "10px 12px"
    height: "46px"
  packet:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
  packet-band-need:
    backgroundColor: "{colors.leaf}"
    textColor: "{colors.on-band}"
    typography: "{typography.packet-title}"
    padding: "12px"
    height: "112px"
  packet-band-want:
    backgroundColor: "{colors.teal}"
    textColor: "{colors.on-band}"
    typography: "{typography.packet-title}"
    padding: "12px"
    height: "112px"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "14px"
  topbar:
    backgroundColor: "{colors.leaf}"
    textColor: "{colors.on-band}"
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
    rounded: "{rounded.panel}"
    padding: "10px 12px"
  flash-success:
    backgroundColor: "{colors.tint-good}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "10px 12px"
  flash-error:
    backgroundColor: "{colors.tint-bad}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "10px 12px"
---

# Design System: Pay My Bill

## Overview

**Creative North Star: "The Seed Packet"**

Every post is a seed packet on a garden-aisle rack: a flat colour band with a plain title, who and where, how far along it is, and what it takes. The packet states what you are helping grow and asks nothing more of the reader. It reads simple and trustworthy, with personality carried by a chunky slab title and the green of the shell, not by decoration.

The system is an operating surface for phones. One narrow column of 608px at most, a leaf-green bar, a pale green ground, white panels with gently cut corners, and no drop shadows. Hierarchy comes from size. Colour is assigned by job: green and teal say what kind of ask it is, marigold says "press this", tomato says "this went wrong or cannot be undone". There is no plant art anywhere; the seed packet is a structure, never an illustration.

The owner's brief rules out four looks: a sad charity page, a bank or finance app, a game or casino, and a generic startup. The light and dark themes follow the system setting and share one shell, so the leaf bar, the colour bands, and marigold stay the same in both.

**Key Characteristics:**
- Flat colour bands in place of pictures; a post with no photo is complete, not missing something.
- Two typefaces: Bitter extra-bold for titles, Public Sans for everything else, including all money.
- A row of ten marks is the one progress device, wherever progress appears.
- One colour for pressing, one for trouble, and neither is used for anything else.
- Depth comes from a white panel on a tinted ground, never from a shadow.

## Colors

A green-on-green world with one warm colour to press and one warm colour for trouble.

### Primary
- **Leaf Green** (#1f5a3d): The top bar, the band on every need, and the browser theme colour. Stays the same in dark mode, where white text on it still holds at 8.1:1.
- **Progress Green** (#1f5a3d light, #62c390 dark): Filled marks, the state-mark dot for a confirmed gift, tab underlines, and the caret. Lightens in dark mode so it stays visible where leaf would sink into the ground.
- **Link Green** (#1f5a3d light, #86d8ac dark): Underlined links in running text.

### Secondary
- **Deep Teal** (#0f5e6e): The band on every want, and nothing else. Holds 7.4:1 under white text, unchanged in dark mode.

### Tertiary
- **Marigold** (#f4b223, hover #e5a412 light, #ffc53d dark): Primary pressable actions only. Its text is always deep ink (#17231c) in both themes.
- **Tomato** (#b8452c light, #f08a72 dark; hover #9d3a24 light, #f5a28e dark): Errors, destructive buttons, and the disputed-gift mark. Its button text is white in light mode and deep ink in dark mode.

### Neutral
- **Pale Leaf Ground** (#e6f0ea light, #0f1a14 dark): The page behind everything.
- **Surface** (#ffffff light, #18251e dark): Panels, packet bodies, form fields, and secondary buttons.
- **Ink** (#17231c light, #edf4ef dark): Headings and body text.
- **Muted** (#46574e light, #a9bcb0 dark): Hints, packet metadata, inactive tabs, and field borders. It clears 6.5:1 on ground and surface in both themes, so it is safe for reading text.
- **Line** (#c3d4ca light, #304238 dark): Dividers between list rows and above the danger zone. Never a field border; it is too faint to mark a control.
- **Empty Mark** (#d2e0d7 light, #304238 dark): The unfilled marks in the growing row. It is a quiet track, so the amount line under the row always states the same fact in words.
- **Info Tint** (#d6e7dd light, #20352a dark): Neutral flashes and notices.
- **Good Tint** (#cfe6d8 light, #1d3d2c dark): Success flashes, earned badges, your own leaderboard row, and pressed reactions.
- **Bad Tint** (#f7dfd8 light, #43241c dark): Error flashes and notices, with ink text.

### Named Rules

**The Marigold Rule.** Marigold appears only on what can be pressed as a primary action, and a panel offers one such decision at a time. A set of equal pay-app choices counts as one decision. The feed has no marigold at all, because the whole packet is the action there.

**The Tomato Rule.** Tomato means an error or a destructive action: field errors, the disputed mark, and the buttons that delete or dispute. It never decorates and never signals urgency on its own.

**The Band Colour Rule.** Leaf means need and teal means want, as flat fills with no gradient or texture. The kind is also stated in words on the packet, so colour is never the only signal.

## Typography

**Display Font:** Bitter 800 (with Georgia, serif)
**Body Font:** Public Sans 400 and 700 (with system-ui, -apple-system, Segoe UI, sans-serif)

**Character:** A heavy slab that looks printed on a packet, beside a plain public-signage sans whose unslashed zeros read cleanly on money. All three files are self-hosted, with `font-display: swap`.

### Hierarchy
- **Display** (800, 2.375rem, 1.15): The post title inside its band on the post page.
- **Headline** (800, 1.75rem, 1.15): Page titles such as Gifts, Leaders, and Log in.
- **Title** (800, 1.25rem, 1.15): Panel and section titles. A nested section title steps down to 1.0625rem.
- **Packet Title** (800, 1.125rem, 1.15): Titles on the feed rack, the brand in the top bar, and form-group legends.
- **List Title** (800, 1.0625rem, 1.2): Post titles in the gift list.
- **Gift Amount** (700, 1.625rem, 1.2): The amount on a gift waiting to be confirmed. Money stays in Public Sans even at title size.
- **Amount** (700, 1.1875rem, 1.5): The raised figure beside the goal in regular weight.
- **Body** (400, 1rem, 1.5): All running text. The 608px column keeps lines readable on a desktop.
- **Label** (700, 1rem, 1.5): Field labels, buttons, tabs, and state emphasis.
- **Hint** (400, 0.9375rem, 1.5): Guidance under headings and inside panels, in muted. Top-bar links use this size at 700.
- **Fine** (400, 0.875rem, 1.5): Packet metadata and state marks, the latter at 700. Field help and field errors use this size too.

Titles use balanced wrapping, and paragraphs and list items use pretty wrapping. Long usernames are cut with an ellipsis in the top bar and on packets. Everywhere else, long text wraps at any character so nothing overflows.

### Named Rules

**The Two Voices Rule.** Bitter 800 is for titles only. Everything else, and all money, is Public Sans at 400 or 700. No other weights are loaded, so none may be requested.

**The Size Carries Rank Rule.** Rank comes from size and the shift of typeface. There is no uppercase, no letterspacing, and no small label above a heading anywhere in the system.

**The Money Lines Up Rule.** Figures in lists and columns are right-aligned with tabular numerals, tight against what they belong to.

## Layout

A single centred column: 640px at most with 16px page padding, leaving 608px of content. The top bar is full-bleed, with its contents aligned to that same 608px. Desktop gets the same column rather than a wider layout; the extra width stays empty ground.

The feed is the one grid. It is the **Seed Rack**, chosen by the owner over a single-column feed: two equal columns on phones and three at 600px and up, with a 10px gap. Packet bodies stretch so the amount lines of neighbouring packets sit level. Bands are at least 112px tall, with the title anchored to the bottom.

Everything else stacks. Spacing steps are 4px within a label and control, 8px between related actions, 10 to 12px between cards and stacked pieces, 14px inside panels and between form fields, 16px at the page edge, and 32px before a new section or the danger zone. Forms are full-width single columns, and paired actions sit side by side and wrap.

Every page must work at 360px without horizontal scroll. Below 400px the top bar tightens its padding and gaps, and its links drop to 0.875rem. Pay-app buttons share a row and wrap at a 96px minimum.

## Elevation & Depth

The system is flat. No element casts a drop shadow. Depth is one tonal step: a surface panel on a tinted ground, in both themes. Inset shadows appear only as state: a 1px inner ring thickens the border of a pressed reaction, and a 6px surface-coloured buffer separates a focused packet's ring from its band.

### Shadow Vocabulary
- **Pressed reaction** (`box-shadow: inset 0 0 0 1px var(--mark)`): Doubles the border weight on a reaction that is on.
- **Packet focus buffer** (`box-shadow: inset 0 0 0 6px var(--surface)`): Keeps the focus ring legible over the dark band.

### Named Rules

**The Flat Packet Rule.** Packets and panels lie flat on the rack. If something needs to stand apart, put it on a surface or give it a band; do not lift it.

## Shapes

One corner does almost all the work: gently cut 6px corners on panels, packets, bands, fields, buttons, and notices. Small elements get proportionate variations: 5px on marks, 4px on earned-badge tags, and a 10px capsule on the top-bar count. Round radio-style dots mark state, and the disputed mark alone is a 2px-cornered square, so it differs in shape as well as colour. Borders are 1.5px on controls, 2px under tabs and above the danger zone, and 1px between list rows. Panels have no border.

### Named Rules

**The Six Pixel Rule.** New containers and controls use the 6px corner. Pill buttons and large rounded cards do not belong to this world.

## Components

### Buttons
Plain, solid, and sure of themselves, like a printed stamp.
- **Shape:** Gently cut corners (6px), at least 44px tall, with 10px 18px padding and a 1.5px border.
- **Primary:** Marigold fill with deep ink text at 700.
- **Secondary:** Surface fill, ink text, muted border. Used for Cancel, "I sent it", "Didn't get it", and the entry points to close or delete.
- **Danger:** Tomato fill. It appears only on the confirming step of a delete or dispute; the step before it is secondary.
- **Hover / Focus:** Fill and border colours shift over 120ms ease-out. A press drops the button 1px. The secondary hover darkens only the border. Focus is the shared 3px ink ring at 2px offset.
- **Disabled:** 55% opacity with a not-allowed cursor.

### Reactions
A secondary button with 8px 14px padding and tabular counts. When on, it takes the good tint and a mark-coloured double border. Visitors who cannot react see the counts as plain muted text instead of a disabled button.

### Seed Packet
The signature container, and the only item in the feed.
- **Structure:** A flat band with the title, then who and where, the growing row, and the amount line.
- **No-photo state (shipped):** The colour band is the complete packet, in leaf or teal by kind. Title in on-band white, packet title size, 12px padding, 112px minimum height.
- **Photo state (planned, not built):** Optional poster photos come in a later story, with the title beneath the picture. No tokens or styles exist for it yet. Until they do, the band is the only packet.
- **Interaction:** The whole packet opens the post, through a link stretched over the title. The username remains its own link above that layer. Hover underlines the title. Focus draws a 3px ink ring just inside the packet edge, with the surface buffer inside it.
- **On the post page:** The band stands alone at full width as a 6px block with the display title and 20px 16px 18px padding. The body sits directly on the ground below it, and panels follow.

### Growing Row
The signature device: ten equal marks that fill left to right, with 4px gaps, always with a text or spoken equivalent.
- **Feed:** 9px tall marks that read as dots at phone width. Filled marks soften to 78% colour so the page does not compete with its titles.
- **Post page:** 13px tall in full colour. Filled marks grow in once on load, 280ms each with a 45ms stagger. Reduced motion shows them filled at once.
- **Profile:** 9px tall and full colour, with no motion, for progress toward the next level.
- **Filling:** Any progress shows at least one mark, and the tenth fills only at 100%.

### Cards / Containers
- **Corner Style:** 6px.
- **Background:** Surface on ground, with no border or shadow.
- **Internal Padding:** 14px for panels and gift cards; 12px 14px for list rows, divided by 1px line.

### Inputs / Fields
- **Style:** Surface fill, 1.5px muted border, 6px corners, 10px 12px padding, at least 46px tall (textareas 120px). The label sits above in 700 and the hint below in muted.
- **Focus:** The 3px ink ring at no offset, and the border turns ink.
- **Error:** A 2px tomato border, with the message below in tomato at 700, linked to the field.
- **Choices:** 20px radios and checkboxes tinted by the theme accent, in 32px rows.

### Navigation
- **Top bar:** Leaf band. Brand at left in Bitter; links at right in 700 and 0.9375rem, with 12px vertical padding for reach. Hover adds a 2px underline. A count of waiting gifts is a white capsule with deep ink text (20px tall, 0.75rem). Focus turns the ring white.
- **Tabs:** 700 muted text over a 2px mark rule. The current tab goes ink with a 4px underline that sits on the rule. A second tab row stacks directly under the first where a page has two filters.
- **Pager:** Plain 700 links, Newer at left and Older at right.

### State Mark
One device for every gift state: a small mark before a 0.875rem, 700 label. It carries no pill or background.
- **Waiting:** Hollow muted ring.
- **Confirmed:** Filled mark-coloured dot.
- **Not received:** Tomato square with tomato text.
- **Expired:** Empty-mark dot with muted text.

### Flashes and Notices
Full-width tinted strips above the content with ink text, 10px 12px padding, and 6px corners: info, success, or error by tint alone. Error flashes are announced as alerts.

## Do's and Don'ts

### Do:
- **Do** treat a band with no picture as the finished packet: flat leaf or teal, with the title anchored at the bottom.
- **Do** make the whole packet open the post, and keep the marigold decision on the post page.
- **Do** keep the Seed Rack at two columns on phones and three at 600px and up.
- **Do** show progress with the ten-mark row and state the same fact in words beside it.
- **Do** use the one state mark for every gift state, differing in shape as well as colour for failures.
- **Do** put one marigold decision in a panel, and make any delete or dispute a two-step move ending in tomato.
- **Do** keep money in Public Sans, with tabular numerals wherever figures are listed in a column.
- **Do** check every new surface in both themes and at 360px wide.

### Don't:
- **Don't** use marigold on anything that is not a primary pressable action, including decoration, highlights, and status.
- **Don't** use tomato for emphasis, urgency, or decoration, and don't set tomato text on the bad tint, where it drops to 4.2:1.
- **Don't** add plant art, leaf motifs, or other seed-packet illustration. The packet is a structure.
- **Don't** render a placeholder or empty image frame for a post with no photo, and don't treat the planned photo state as shipped.
- **Don't** drift toward a sad charity page, a bank or finance app, a game or casino, or a generic startup.
- **Don't** add drop shadows, gradients, pill buttons, or small uppercase labels above headings.
- **Don't** load another weight or typeface, or set money in Bitter.
- **Don't** extend the reaction emoji into a general icon set. They are the content of those two reactions and nothing more.
