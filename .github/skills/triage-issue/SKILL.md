---
name: triage-issue
description: >
  Triage and classify new issues for the CSC database repository.
  Use this skill whenever an issue is opened, assigned to you, or needs
  classification. Trigger on: new issue triage, "classify this issue",
  "what type of issue is this", labelling requests, issue assignment,
  data correction reports, data addition requests, bug reports, feature
  requests, or any time you need to categorise, label, prioritise, or
  respond to a GitHub issue. Also use when deciding whether an issue
  can be auto-fixed or needs human intervention.
---

## Triage Process

### Step 1: Classify the Issue

Read the issue title and description to determine the category:

| Category | Labels | Indicators |
|----------|--------|------------|
| Data Correction | `data-correction` | "wrong", "incorrect", "outdated", "fix coordinates" |
| Data Addition | `data-addition` | "add", "missing", "new city/state", "not in database" |
| Bug Report | `bug` | "error", "crash", "not working", "broken" |
| Feature Request | `enhancement` | "would be nice", "please add", "feature", "suggestion" |
| Question | `question` | "how to", "is it possible", "what is", "?" |
| Documentation | `documentation` | "docs", "readme", "instructions", "guide" |

### Step 2: Add Entity Labels

If the issue involves specific data entities, add:
- `data:cities` - for city-related issues
- `data:states` - for state-related issues
- `data:countries` - for country-related issues

### Step 3: Assess Severity

| Severity | Label | Criteria |
|----------|-------|----------|
| Critical | `critical` | Country/state deletion, widespread data corruption |
| High | `priority:high` | Many cities affected, coordinate errors for major cities |
| Normal | (no label) | Individual city corrections, small additions |
| Low | `priority:low` | Cosmetic changes, optional field additions |

### Step 4: Determine Action

**Auto-fixable issues** (label `auto-fix`; assignment to @copilot is manual, no workflow does it):
- Simple coordinate corrections with source provided
- Missing optional fields that can be looked up
- Formatting issues in existing data
- Single record corrections with clear correct values

**Needs contributor** (label `help-wanted`):
- Large data additions requiring local knowledge
- Corrections without source documentation
- Issues in regions/countries where verification is difficult

**Needs maintainer** (assign to @dr5hn):
- Schema changes
- API-related issues
- Infrastructure/tooling issues
- State or country level changes
- Policy decisions

### Step 5: Respond to the Issue

For data corrections:
```
Thanks for reporting this! I've classified this as a data correction for [entity type].

[If auto-fixable]: I'll work on a fix for this. A PR will be opened shortly.
[If needs contributor]: Would you like to submit a PR with this fix? Here's how:
1. Edit the relevant file in `contributions/` directory
2. Submit a PR with a link to an official source

You can also use our [CSC Update Tool](https://manager.countrystatecity.in/) for a guided process.
```

For data additions:
```
Thanks for requesting this addition!

To help us process this, please provide:
- The data in JSON format with required fields
- A link to an official source
- The number of records

Refer to our [Contribution Guidelines](https://github.com/dr5hn/countries-states-cities-database/blob/master/.github/CONTRIBUTING.md) for the required fields.
```

For bug reports:
```
Thanks for reporting this bug. I've tagged it for review.

[If additional info needed]: Could you please provide:
- Steps to reproduce
- Expected vs actual behaviour
- Which platform/tool you're using (API, JSON files, npm package)
```

## Important Rules

- Always be polite and welcoming
- Do not close issues without maintainer approval
- Do not make promises about timelines
- For API issues, direct users to api@countrystatecity.in
- For urgent data issues, apply the `priority:high` label
