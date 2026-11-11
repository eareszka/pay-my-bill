# Threat Model & Abuse Cases

| # | Abuse case | Actor | Mitigation | Sprint |
|---|---|---|---|---|
| T1 | Fake "I sent it" to farm XP or leaderboard rank | Donor | Confirmed-only scoring (ADR 0004) | 2 |
| T2 | Sock-puppet ring confirming each other's donations | Colluding accounts | Verified email required; 3-day account-age gate for boards; per-pair weekly cap ($200) with admin flag; per-IP signup limit (#137); admin queue flags donors when 3+ of the people they helped got gifts only from them and joined within 24 hours (#140) | 1, 5 |
| T3 | Business, startup, or investment fundraising | Poster | $1,000 ask cap; at most 2 open posts; keyword flag → review queue; reports; bans | 1, 5 |
| T4 | Scam posts (fake sob stories) | Poster | Reports; admin removal; repeat-dispute flags; visible poster history | 5 |
| T5 | Harassment in posts or thank-yous | Any | Reports; admin removal; Community Rules | 5 |
| T6 | Account takeover changes payment handles | Attacker | Hashed passwords; email notice when a handle changes; rate-limited login | 1 |
| T7 | Malicious upload (post photo, later thank-you photo) | Any | 8 MB and 40-megapixel limits checked before decoding; only JPEG, PNG, or WebP; every photo re-encoded to WebP by Pillow, so the stored file is never the upload; random filenames; served from R2 or a fixed-pattern route, never executable (ADR 0015) | 5 |
| T8 | XSS / CSRF | Attacker | Jinja autoescaping; CSRF tokens on all forms | 1 |
| T9 | Leaked secrets | Developer error | `.env` is gitignored; gitleaks pre-commit hook; env-only config | 0 |
| T10 | Location privacy | — | Region is self-reported (city/state only); no GPS | 1 |
| T11 | Round-tripping money between accounts to climb leaderboards | Colluding accounts | Rank by distinct recipients helped, not dollars (ADR 0009); per-pair weekly cap flag | 3 |
| T12 | Post, collect, and vanish | Poster | Required results update within 7 days; overdue blocks new posts; follow-through stat on profile (ADR 0008) | 4 |
| T13 | Minors on the platform | Under-18 user | 18+ attestation at signup; ToS states the age rule; accounts removed when reported | 2 |
| T17 | Harmful or identifying photos: nudity, other people, documents, or hidden location data | Poster | Location and camera data stripped on upload; the post form asks for no personal details; "Inappropriate photo" report reason; admins remove the photo alone or the whole post; deleting a post or account deletes its photos (ADR 0015) | 5 |
| T16 | Fake feedback to reach the top of the board | Poster, friends | Only gifts and reactions from accounts verified and 3+ days old when they acted count, positive feedback needs a counted update and is capped, 🤨 can't be erased, and overdue posters are out (ADR 0013). Stronger limits come with the admin queue | Later |
| T14 | Sensitive health or financial details exposed in posts or updates | Poster (self) | Privacy note on the post form; receipts never required (ADR 0008); edit and delete for posts and accounts | 2 |
| T15 | Donations left `pending` forever, so donors never get credit | Recipient (neglect) | Confirm reminders; auto-expire `pending` after 14 days with no credit | 2 |
