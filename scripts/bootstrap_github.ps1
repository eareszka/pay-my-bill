# One-time GitHub setup for Pay My Bill. Run from the repo root after `gh auth login`.
# Creates the private repo, labels, milestones, and protects main. Safe to re-run.
# Requires token scopes: repo, workflow (gh auth refresh -s workflow,project).
$ErrorActionPreference = "Stop"

git remote get-url origin *> $null
if ($LASTEXITCODE -ne 0) {
    gh repo create pay-my-bill --private --source . --remote origin `
        --description "Community app for everyday wants and needs - not for business fundraising"
}
git push -u origin main
if ($LASTEXITCODE -ne 0) { throw "Push failed. Run: gh auth refresh -s workflow,project" }

$labels = @(
    @("type:story", "1d76db"), @("type:bug", "d73a4a"), @("type:chore", "cfd3d7"), @("type:epic", "5319e7"),
    @("priority:P0", "b60205"), @("priority:P1", "d93f0b"), @("priority:P2", "fbca04"), @("priority:P3", "c2e0c6"),
    @("points:1", "ededed"), @("points:2", "ededed"), @("points:3", "ededed"), @("points:5", "ededed"), @("points:8", "ededed"),
    @("epic:accounts", "0e8a16"), @("epic:posts", "0e8a16"), @("epic:donations", "0e8a16"),
    @("epic:rewards", "0e8a16"), @("epic:leaderboards", "0e8a16"), @("epic:safety", "0e8a16"),
    @("sprint:01", "bfdadc")
)
foreach ($l in $labels) { gh label create $l[0] --color $l[1] --force }

# Quote API paths: bare {owner} is a PowerShell script block.
$existing = gh api 'repos/{owner}/{repo}/milestones?state=all' --jq '.[].title'
foreach ($m in @("v0.1-alpha", "v0.2-beta", "v1.0")) {
    if ($existing -notcontains $m) { gh api 'repos/{owner}/{repo}/milestones' -f "title=$m" | Out-Null }
}

# Branch protection: PRs required, CI must pass. Needs a public repo or GitHub Pro for private repos.
$protection = @'
{
  "required_status_checks": { "strict": true, "contexts": ["checks"] },
  "enforce_admins": false,
  "required_pull_request_reviews": { "required_approving_review_count": 0 },
  "restrictions": null
}
'@
$protection | gh api -X PUT 'repos/{owner}/{repo}/branches/main/protection' --input -
if ($LASTEXITCODE -ne 0) { Write-Warning "Branch protection needs GitHub Pro on private repos; enforce PR-only by convention." }

Write-Host "Done. For the Projects board run: gh auth refresh -s project"
