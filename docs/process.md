# Development Process

## Cadence: 1-week sprints, Monday to Sunday
| Ceremony | When | Output |
|---|---|---|
| Sprint Planning | Monday, 30 min | `docs/sprints/sprint-NN.md`: goal, committed stories, points |
| Daily check-in | Each work session | One line in the sprint file: done / next / blocked |
| Backlog Refinement | Thursday, 20 min | Next sprint's stories meet the Definition of Ready |
| Sprint Review | Sunday | Demo evidence; each story accepted or rejected against its acceptance criteria |
| Retrospective | Sunday | Keep / Change / Try, with at most one action item |

**Estimation:** Fibonacci points (1, 2, 3, 5, 8). Split anything bigger than 8. Track velocity in `sprints/velocity.md`.

## Definition of Ready
- User story with testable Given/When/Then acceptance criteria
- Estimated, with dependencies identified
- Wireframe or sketch attached for UI stories

## Definition of Done
- Merged to `main` through a PR, with CI green (ruff, mypy, pytest, pip-audit)
- New logic is unit tested and coverage isn't lowered (≥80% overall)
- Acceptance criteria demonstrated at phone width
- README / ADR / CHANGELOG updated as needed
- No open P0 or P1 bugs against the story

## Git workflow
- GitHub Flow: `main` is protected and only changes through PRs; PRs are squash-merged.
- Branch names: `feat/<issue#>-name`, `fix/<issue#>-name`, `chore/<issue#>-name`
- Conventional Commits: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`, with `Closes #N` in the PR
- Review: self-review plus `/code-review` on every PR
- Releases: SemVer tags and a `CHANGELOG.md` in Keep-a-Changelog format

## Environments
- **dev:** local SQLite with `seed.py` fake data
- **staging:** Fly.io (or Render) with Postgres; auto-deploys from `main`
- **prod:** promoted from release tags, from v0.2-beta onward

## Labels
`type:story|bug|chore|epic` · `priority:P0–P3` · `points:1|2|3|5|8` · `epic:<name>` · `sprint:NN`
