# ADR 0017: The product is named Yearnly

**Status:** Accepted · **Date:** 2026-11-14 · **Closes:** #35 (PB-10)

## Context
"Pay My Bill" was a working name. It can't ship: an app called "Pay My Bill" is already on the App Store, where names must be unique, and older PAYMYBILL marks cover bill payment. The name also undersells the product, which is for wants as well as needs. A name that sends email from its own domain is also needed, because Outlook drops mail sent through Brevo with a Gmail From address.

## Options considered
Each was checked for `.com` and `.app` availability (RDAP), App Store and Google Play conflicts, and trademark filings.
- **Chip In:** the product's own verb, but chipin.com and chipin.app are taken, an app named "Chip In" is listed, ChipInPool and Beyond's Chip-In sit beside it, and the everyday phrase is hard to protect.
- **Chip Along:** both domains free and no conflicts, but it stays close to the crowded "chip in" space.
- **Penny Wish, Wants Met, Small Wants:** clear, but "Wish" names sit near the WISH shopping marks, and "Wants & Needs" apps already exist.
- **Upswing, Pay My Bill:** existing apps and live marks.

## Decision
The product is **Yearnly**: from "yearn", the wanting behind every ask, big or small.
- **Primary domain:** `yearnly.app`. Also register `getyearnly.com` and redirect it, since people type `.com` by habit. `yearnly.com` was registered by someone else in January 2026 and isn't needed.
- **Email** goes out from `no-reply@yearnly.app` through Brevo, with SPF, DKIM, and DMARC set on the domain. `support@yearnly.app` forwards to the owner.
- **"Chip in" stays the in-app verb** for giving. The name is the brand, and the button says what you do.
- **App Store:** list as "Yearnly" if the name is free in App Store Connect, otherwise with a short descriptor (for example "Yearnly: Chip In").

## Consequences
- The rename (wordmark, page titles, emails, Terms and Privacy, manifest, icon, PRODUCT.md, DESIGN.md) is its own Sprint 6 story, done through Impeccable. Until then, the UI still says Pay My Bill.
- `APP_URL`, `MAIL_FROM`, and `CONTACT_EMAIL` move to the new domain once DNS, Brevo, and Render's custom domain are set up.
- Search checks found no app, company, or mark named Yearnly; the nearest are "Yarnly" (a knitting app) and several "Yearly" calendar apps, which are different words in different fields. The owner confirms in USPTO Trademark Search and the app stores before buying.
