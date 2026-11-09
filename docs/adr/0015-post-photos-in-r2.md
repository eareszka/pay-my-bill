# ADR 0015: Post photos are re-encoded and stored in Cloudflare R2

**Status:** Accepted · **Date:** 2026-11-09

## Context
The owner wants posters to add a photo of what they need, and chose the full upload story over a design-only preview. Render's free instance has no persistent disk, so uploads saved there vanish on every deploy. Storing images in Neon's free Postgres (0.5 GB) would fill it after about 2,000 photos and slow backups. Photos also carry risk: phone photos embed GPS location (the product promises no GPS, T10), uploads can be malformed or hostile (T7), and a photo can show something harmful (T17).

## Decision
- **One optional photo per post.** It's added on the post form. The poster can remove it, and an admin can remove it alone or with the post. Replacing it waits for post editing (#116).
- **Every upload is rebuilt.** Uploads must be JPEG, PNG, or WebP, at most 8 MB and 40 megapixels, checked before decoding. Pillow turns the image upright, shrinks it to at most 1600px on its longest edge, and saves a fresh WebP with no metadata. The upload itself is never stored.
- **Storage is Cloudflare R2** (S3 API, 10 GB free, no egress fees) when `R2_BUCKET` is set. Photos are read straight from the bucket's public URL under random `posts/<32 hex>.webp` keys. Without a bucket (local dev and tests), photos go to `PHOTO_DIR` and are served by `/media/<key>`, which only answers keys in that exact pattern.
- **Photos show right away and can be reported.** "Inappropriate photo" is a new report reason. The post's text still goes through the fundraising keyword check.
- **Deletes follow the database.** Deleting a post or account drops the photo key in the same transaction, then deletes the file after commit. A failed file delete is logged, never shown to the user.

## Consequences
- Staging and production need a Cloudflare account, an R2 bucket with public access, and five settings (`R2_*`). Until those are set, staging stores photos on its own disk, and they're lost on the next deploy.
- No photo is reviewed before it's seen. Reports and admin removal are the safety net, as with post text.
- boto3 and Pillow join the dependencies, and Pillow security releases need watching (pip-audit runs in CI).
- The migration adds `posts.photo_key` and the `photo` report reason. It follows 0012. If #116's migration 0013 merges first, this one must be re-pointed to 0013.
