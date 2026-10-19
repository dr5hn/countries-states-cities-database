# CSC Repository Automation - Setup Guide

## Quick Start

### Step 1: Copy files to your repository

Unzip `csc-github-automation.zip` into your repository root. This adds/updates the `.github/` directory and creates a `CHANGELOG.md`.

```bash
# From your repo root
unzip csc-github-automation.zip -d .
```

### Step 2: Push the files

Push the files to your default branch:

```bash
git add .github/ CHANGELOG.md
git commit -m "feat: add repository automation workflows"
git push origin master
```

This repository's labels already exist. The one-time label workflow was removed after it had done its job.

### Step 3: Add Slack webhook (optional but recommended)

1. Go to your Slack workspace > **Apps** > search **Incoming Webhooks**
2. Create a new webhook pointed at your desired channel (e.g., `#csc-repo-activity`)
3. Copy the webhook URL
4. In your GitHub repo: **Settings** > **Secrets and variables** > **Actions** > **New repository secret**
5. Name: `SLACK_WEBHOOK_URL`, Value: paste the webhook URL

### Step 4: Verify Copilot access

Since you have Copilot Pro (free OSS maintainer):
1. Go to repo **Settings** > **Copilot** > **Coding agent** > ensure it is enabled
2. The skills in `.github/skills/` and agents in `.github/agents/` will be auto-detected
3. Test by creating an issue and assigning it to `@copilot`

### Step 5: Install dependencies (for local testing)

```bash
cd .github/scripts
npm install
```

The `node_modules/` directory is gitignored and installed fresh by GitHub Actions on each run.

---

## Potential Blockers and Solutions

### Blocker 1: Branch Protection Rules

**Problem:** A workflow that pushes directly to a protected default branch fails.

**Solution:** None needed here. The weekly changelog update in `weekly-digest.yml` opens a PR (branch `changelog/weekly-<date>`) instead of pushing, and `auto-changelog.yml` only sends a Slack message.

### Blocker 2: Missing Data Files for Cross-Reference

**Problem:** The cross-reference validation (`validate-cross-reference.js`) tries to load `countries.json` and `states.json` from the repo root, `json/`, or `data/` directories. If these files are not in any of those paths, cross-reference checks will be skipped.

**Solution:** Verify your repo has these files in one of: `./countries.json`, `./json/countries.json`, or `./data/countries.json` (same for states.json). If they are in a different location, update the `loadRepoData()` function in `.github/scripts/utils.js`:

```javascript
const possiblePaths = [
  path.join(process.cwd(), `${entityType}.json`),
  path.join(process.cwd(), 'json', `${entityType}.json`),
  path.join(process.cwd(), 'data', `${entityType}.json`),
  // Add your custom path here:
  path.join(process.cwd(), 'your-path', `${entityType}.json`),
];
```

### Blocker 3: Contributions Directory Structure

**Problem:** The validation scripts determine entity type from the file path by looking for "cities", "states", or "countries" in the path string. If your `contributions/` directory uses a different naming convention, entity detection will fail.

**Expected structure (any of these work):**
```
contributions/cities/some-file.json     # Detected as cities
contributions/cities.json               # Detected as cities
contributions/IN/cities/mumbai.json     # Detected as cities
contributions/add-cities-india.json     # Detected as cities (has "cities" in name)
```

**Will NOT work:**
```
contributions/new-data.json             # Cannot determine entity type
contributions/IN/maharashtra.json       # No entity keyword in path
```

**Solution:** Ensure contribution files have the entity type ("cities", "states", or "countries") somewhere in the file path or filename.

### Blocker 4: GitHub Actions Minutes

**Problem:** The PR validator runs multiple Node.js scripts per PR. Each run uses approximately 1-2 minutes of GitHub Actions time.

**Solution:** Public repositories get unlimited free Actions minutes. Since `dr5hn/countries-states-cities-database` is public, this is not an issue. If you ever make it private, be aware of the 2,000 minutes/month limit on the free tier.

### Blocker 5: Country Bounds Coverage

**Problem:** The `country-bounds.json` file contains bounding boxes for ~160 countries. Countries/territories not in this file will skip the coordinate bounds check silently.

**Solution:** The check is non-blocking (warning only), so missing bounds will not reject valid PRs. To add bounds for additional countries, edit `.github/data/country-bounds.json` (one box, or an array of boxes for remote territories; see [Updating Country Bounds](#updating-country-bounds)):

```json
{
  "XX": {
    "minLat": -90,
    "maxLat": 90,
    "minLon": -180,
    "maxLon": 180
  }
}
```

### Blocker 6: Existing PR Template Conflict

**Problem:** If you already have a `.github/PULL_REQUEST_TEMPLATE.md`, this will overwrite it.

**Solution:** Review the new template and merge any existing content you want to keep before committing.

### Blocker 7: Large Repository Checkout Time

**Problem:** The PR validator uses `fetch-depth: 0` (full clone) for diff analysis. On a large repo, this can be slow.

**Solution:** If checkout time becomes an issue, change to `fetch-depth: 1` in the workflow. This will still work for most validations but may limit some diff analysis features. The cross-reference validation loads JSON files from the checked-out repo, so having the full tree is important.

### Blocker 8: Rate Limits on Source URL Checks

**Problem:** The source URL checker makes HTTP HEAD requests to verify URLs. Some websites block automated requests or rate-limit them.

**Solution:** The checker is limited to 5 URLs per PR and has a 10-second timeout. Results are warnings only (non-blocking). If a legitimate source URL fails the check, it will not prevent the PR from being reviewed.

### Blocker 9: Concurrent PR Updates

**Problem:** If multiple commits are pushed rapidly to a PR, multiple workflow runs may start. The concurrency group setting cancels older runs, but the validation comment might briefly show stale results.

**Solution:** Already handled - the workflow has `cancel-in-progress: true` in the concurrency group, ensuring only the latest run completes and posts results.

---

## File Reference

### Workflows (`.github/workflows/`)

| File | Trigger | Purpose |
|------|---------|---------|
| `pr-validator.yml` | PR opened/edited/sync | All validation checks, auto-labelling, report comment |
| `issue-autoassign.yml` | Issue labelled `data-correction` | Comment a checklist on a sparse report, add `help-wanted` |
| `stale-cleanup.yml` | Weekly (Sunday) | Warn/close inactive PRs, remove stale label on activity |
| `weekly-digest.yml` | Weekly (Monday 9am IST) | Slack summary of repo status; opens the weekly `CHANGELOG.md` PR |
| `auto-changelog.yml` | PR merged | Slack message for each merged PR |

### Scripts (`.github/scripts/`)

| File | Purpose |
|------|---------|
| `utils.js` | Shared: schema definitions, validation functions, formatting |
| `validate-pr-format.js` | Check PR description, source, issue linkage |
| `validate-schema.js` | JSON lint + field validation against schema.sql |
| `validate-cross-reference.js` | FK integrity: state_id, country_id, code matching |
| `validate-coordinates.js` | Coordinate bounds within parent country |
| `detect-duplicates.js` | Fuzzy name + proximity duplicate detection |
| `analyse-diff.js` | Auto-label entity types, detect critical changes, count records |
| `check-source-urls.js` | HTTP HEAD check on source URLs in PR description |
| `slack-notify.js` | Slack message builder and sender |

### Copilot Skills (`.github/skills/`)

| Skill | When Copilot Uses It |
|-------|---------------------|
| `validate-contribution` | Asked to validate/check/review a contribution |
| `fix-contribution` | Asked to fix/correct issues in a PR |
| `review-data-pr` | Asked to review a data PR for quality |
| `triage-issue` | Asked to classify/triage an issue |

### Copilot Agents (`.github/agents/`)

| Agent | Purpose |
|-------|---------|
| `data-reviewer` | Specialised PR reviewer for data contributions |
| `contributor-helper` | Helps contributors fix issues, responds to questions |

### Templates

| File | Purpose |
|------|---------|
| `PULL_REQUEST_TEMPLATE.md` | Structured PR template with required fields |
| `ISSUE_TEMPLATE/data_correction.yml` | Structured data correction report |
| `ISSUE_TEMPLATE/data_addition.yml` | Structured data addition request |
| `ISSUE_TEMPLATE/bug_report.yml` | Bug report template |

---

## Testing Locally

You can test validation scripts locally before deploying:

```bash
cd .github/scripts
npm install

# Set required env vars
export GITHUB_TOKEN="your-github-pat"

# Test individual scripts (requires being run in repo root context)
cd ../../
node .github/scripts/validate-schema.js
```

Note: Scripts that use `@actions/github` will need a valid GitHub context to run properly. For local testing, you may need to mock the context or use the GitHub CLI.

---

## Maintenance

### Adding New Validation Rules

1. Add the rule to `.github/scripts/utils.js` (SCHEMA object) or create a new script
2. Add a new step in `pr-validator.yml`
3. Add the outputs to the report generation step
4. Update the Copilot skills if the rule affects validation guidance

### Updating Country Bounds

Edit `.github/data/country-bounds.json`. A country entry is either one box or, for a country with remote
territories, an array of boxes (the first is the main territory):
```json
"XX": { "minLat": -90, "maxLat": 90, "minLon": -180, "maxLon": 180 },
"ES": [
  { "minLat": 36.0, "maxLat": 43.79, "minLon": -9.3, "maxLon": 4.33 },
  { "minLat": 27.6, "maxLat": 29.5, "minLon": -18.2, "maxLon": -13.3 }
]
```
A box whose `minLon` is greater than its `maxLon` crosses the 180° meridian (Russia, Fiji): longitudes from
`minLon` east to 180 and from -180 east to `maxLon` are inside it; the 0.45° tolerance wraps across 180° too.
Keep remote-territory boxes tight, one per island group: a single box spanning the ocean between territories
also admits the neighbouring countries (one box over all of France's Indian Ocean islands took in Madagascar).
The check is `isWithinBounds()` in `.github/scripts/utils.js`, with unit tests in `utils.test.js`.

### Modifying Slack Notifications

Edit `.github/scripts/slack-notify.js` to change message formats, colours, or add new notification types.

### Adjusting Stale Thresholds

In `.github/workflows/stale-cleanup.yml`, modify `WARNING_DAYS` (default: 21) and `CLOSE_DAYS` (default: 30).
