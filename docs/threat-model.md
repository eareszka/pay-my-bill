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
