# ADR 0020: Up to five photos per post, the first one required

**Status:** Accepted · **Date:** 2026-11-18 · Supersedes the "one optional photo" part of ADR 0015

## Context
The owner wants the new-post questions to end like dating-app onboarding: five photo boxes, at least one photo required (#279). ADR 0015 allowed one optional photo, stored in `posts.photo_key`, which the feed card, post page, admin queue, home mosaic, and every delete path read.

## Decision
- **One to five photos per new post.** The photo step has five boxes, each its own file input named `photos`. Empty boxes are skipped. At least one photo is required, and the first one chosen is the cover.
- **The cover stays in `photo_key`, the rest go in `more_photo_keys`** (a JSON list of up to four keys, `[]` by default). Everything that shows one photo (feed card, home mosaic, preload) keeps reading the cover. The post page and admin queue show them all.
- **Every photo follows ADR 0015's rules:** re-encoded WebP, location removed, 8 MB and 40 megapixels each, stored in R2. The request limit for the new-post form rises to 41 MB.
- **Deletes take every photo.** `Post.take_photos()` clears both columns and returns the keys. Deleting or scrubbing a post, Remove photos, admin removal, bans, and account deletion all use it, then discard each key after commit, with the #149 retry queue as before. If storage fails partway through a new post, the photos already saved are discarded.
- **Existing posts are unchanged.** Posts with no photo or one photo still work, and editing a post still doesn't change its photos.
- The CSP allows `blob:` images, so each box can preview the photo picked for it before upload.

## Consequences
- R2 use can grow up to five times per post. At about 200 KB per WebP, 10 GB still holds about 50,000 photos.
- A 41 MB upload is slow on a weak connection, and Pillow decodes the photos one at a time (#155), so a five-photo post takes longer to submit.
- If the server rejects the form, the browser can't refill file inputs, so the poster picks the photos again.
- Migration 0023 adds `posts.more_photo_keys`.
