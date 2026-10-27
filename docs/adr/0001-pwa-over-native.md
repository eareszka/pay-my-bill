# ADR 0001 — PWA over native apps

**Status:** Accepted · **Date:** 2026-10-27

## Context
We need to reach phone users fast, with one developer, and iterate weekly.

## Decision
Ship a mobile-first Progressive Web App (installable, with an offline app shell). Defer native apps.

## Consequences
- One codebase, instant deploys, and no App Store review. Apple's review is strict about donation and payment apps.
- Push notifications on iOS are limited to installed PWAs.
- The PWA can be wrapped (for example with Capacitor) later if a native presence is needed.
