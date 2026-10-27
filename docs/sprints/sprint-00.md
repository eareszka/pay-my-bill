# Sprint 0 — Foundation

**Dates:** 2026-10-27 → 2026-11-01 · **Goal:** a professional delivery pipeline in place before any feature code

## Committed
| Item | Points | Status |
|---|---|---|
| Repo, .gitignore, pyproject (ruff/mypy/pytest), pre-commit | 2 | Done |
| CI workflow (lint, types, tests, audit) | 2 | Done |
| Issue and PR templates; labels; milestones | 1 | Done |
| PRD, ADRs 0001–0004, threat model, process doc | 3 | Done |
| App factory + `/health` + first test, CI green | 1 | Done (green on GitHub) |
| GitHub Projects board | 1 | Done: github.com/users/eareszka/projects/4 |
| Staging deploy serving `/health` | 2 | Done: https://pay-my-bill-staging.onrender.com/health returns 200 (Render, ADR 0005) |
| Sprint 1 stories written to the Definition of Ready | 2 | Done: issues #1–#7, all in Ready |

## Daily log
- 2026-10-27: Scaffolded the repo, tooling, docs, and skeleton app. Next: GitHub repo, labels, Sprint 1 issues.
- 2026-10-27: Pushed to the private GitHub repo; CI is green. Milestones, the Projects board, and Sprint 1 issues are created. Blocked: branch protection needs GitHub Pro on a private repo, so PR-only is enforced by convention. Next: staging deploy.
- 2026-10-27: Merged PR #8. Claimed #9; added `render.yaml` (gunicorn + free Postgres), ADR 0005, and deploy notes. Next: merge, connect the Blueprint in Render, verify `/health`. Blocked: connecting the repo needs Emery's Render account.
- 2026-10-27: Merged PR #10; Emery connected the Render Blueprint. Verified `GET /health` returns 200 `{"status":"ok"}` at the staging URL. All Sprint 0 items are done. Next: Sprint 0 Review and Retro on Sunday.

## Review
_(Sunday)_

## Retro
_(Sunday: Keep / Change / Try)_
