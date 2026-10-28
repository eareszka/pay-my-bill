# Threat Model & Abuse Cases

| # | Abuse case | Actor | Mitigation | Sprint |
|---|---|---|---|---|
| T1 | Fake "I sent it" to farm XP or leaderboard rank | Donor | Confirmed-only scoring (ADR 0004) | 2 |
| T2 | Sock-puppet ring confirming each other's donations | Colluding accounts | Verified email required; 3-day account-age gate for boards; per-pair weekly cap ($200) with admin flag | 1, 5 |
| T3 | Business, startup, or investment fundraising | Poster | $1,000 ask cap; at most 2 open posts; keyword flag → review queue; reports; bans | 1, 5 |
| T4 | Scam posts (fake sob stories) | Poster | Reports; admin removal; repeat-dispute flags; visible poster history | 5 |
| T5 | Harassment in posts or thank-yous | Any | Reports; admin removal; Community Rules | 5 |
| T6 | Account takeover changes payment handles | Attacker | Hashed passwords; email notice when a handle changes; rate-limited login | 1 |
| T7 | Malicious upload (thank-you photo) | Any | Image type and size validation; random filenames; served from a non-executable path | 4 |
| T8 | XSS / CSRF | Attacker | Jinja autoescaping; CSRF tokens on all forms | 1 |
| T9 | Leaked secrets | Developer error | `.env` is gitignored; gitleaks pre-commit hook; env-only config | 0 |
| T10 | Location privacy | — | Region is self-reported (city/state only); no GPS | 1 |
| T11 | Round-tripping money between accounts to climb leaderboards | Colluding accounts | Rank by distinct recipients helped, not dollars (ADR 0009); per-pair weekly cap flag | 3 |
| T12 | Post, collect, and vanish | Poster | Required results update within 7 days; overdue blocks new posts; follow-through stat on profile (ADR 0008) | 4 |
| T13 | Minors on the platform | Under-18 user | 18+ attestation at signup; ToS states the age rule; accounts removed when reported | 2 |
| T14 | Sensitive health or financial details exposed in posts or updates | Poster (self) | Privacy note on the post form; receipts never required (ADR 0008); edit and delete for posts and accounts | 2 |
| T15 | Donations left `pending` forever, so donors never get credit | Recipient (neglect) | Confirm reminders; auto-expire `pending` after 14 days with no credit | 2 |
