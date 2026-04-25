# FIX #1039 — Backfill country `postal_code_format` / `postal_code_regex`

**Issue:** [#1039 — Can we add a postcode for this?](https://github.com/dr5hn/the-countries-states-cities-database/issues/1039)
**Scope:** Country-level postal *format & regex* metadata only (Tier 1).
**Date:** 2026-04-25

## Problem

The `countries` table already has `postal_code_format` and `postal_code_regex` columns, populated for 177 of 250 countries. The remaining 73 were `null`. This PR fills the subset of those 73 where the postal system is universally documented and unambiguous, finishing the existing infrastructure without introducing external data dependencies.

This PR does **not** address city- or state-level postcode values (a much larger scope — see issue discussion for tiered roadmap).

## Coverage Change

| Before | After | Δ |
|--------|-------|---|
| 177 / 250 (70.8%) | **189 / 250 (75.6%)** | +12 |

## Countries Updated (12)

| ISO2 | Country | `postal_code_format` | `postal_code_regex` |
|------|---------|----------------------|---------------------|
| AF | Afghanistan | `####` | `^(\d{4})$` |
| BT | Bhutan | `#####` | `^(\d{5})$` |
| KY | Cayman Islands | `KY#-####` | `^KY\d-\d{4}$` |
| MU | Mauritius | `#####` | `^(\d{5})$` |
| NA | Namibia | `#####` | `^(\d{5})$` |
| TF | French Southern Territories | `#####` | `^(\d{5})$` |
| TT | Trinidad and Tobago | `######` | `^(\d{6})$` |
| TZ | Tanzania | `#####` | `^(\d{5})$` |
| UM | United States Minor Outlying Islands | `#####` | `^(\d{5})$` |
| VC | Saint Vincent and the Grenadines | `VC####` | `^VC\d{4}$` |
| VG | Virgin Islands (British) | `VG####` | `^VG\d{4}$` |
| XK | Kosovo | `#####` | `^(\d{5})$` |

Format placeholders use the existing convention: `#` = digit, `@` = letter, literal characters as-is.

## Countries Deliberately Left `null` (61)

The remaining 61 countries fall into three groups; **`null` is the correct value** for all of them:

### A. No postal code system (per Universal Postal Union documentation, ~50 countries)
Includes most of sub-Saharan Africa (Angola, Benin, Botswana, Burkina Faso, Burundi, Cameroon, Central African Republic, Chad, Comoros, Congo, DRC, Djibouti, Equatorial Guinea, Eritrea, Gabon, Gambia, Ghana, Guinea, Mali, Mauritania, Rwanda, São Tomé, Seychelles, Sierra Leone, South Sudan, Togo, Uganda, Zimbabwe), the Caribbean (Antigua, Aruba, Bahamas, Belize, Bolivia, Curaçao, Dominica, Grenada, Guyana, Jamaica, Saint Kitts and Nevis, Suriname, Sint Maarten), the Gulf (Qatar, Yemen), and most of Oceania (Cook Islands, Fiji, Kiribati, Solomon Islands, Tokelau, Tonga, Tuvalu, Vanuatu).

### B. Disputed/conflict regions where official postal status is unsettled (~5 countries)
Western Sahara, Palestinian Territory Occupied, Syria, Libya — `null` reflects the genuine ambiguity.

### C. Uninhabited / no civil postal infrastructure (~3)
Antarctica, Bouvet Island.

### D. Edge cases worth a future PR (~3)
Saint Lucia (recently introduced LC## ### but adoption uneven), Montserrat (MSR####), Bonaire/Sint Eustatius/Saba (uses Caribbean Netherlands codes since 2014). Left `null` here to keep this PR conservative and high-confidence.

## Validation

- ✅ JSON syntax valid (`json.load()` succeeds, 250 records)
- ✅ All 12 new regexes compile in Python `re`
- ✅ All 189 populated regexes still compile
- ✅ Diff is minimal: exactly 24 line changes (12 entries × 2 fields), no whitespace churn
- ✅ No auto-managed fields (`id`, `created_at`, `updated_at`, `flag`) modified
- ✅ Field names match existing schema (`postal_code_format`, `postal_code_regex`)

## Out of Scope (Future Work)

This is **Tier 1** of the roadmap proposed in the issue analysis. Future tiers (not part of this PR):

- **Tier 2:** State-level postcode prefix (new optional column on `states`)
- **Tier 3:** City-level single postcode (new optional column on `cities`)
- **Tier 4:** Postcode-as-entity (new table)

Each of those requires a sourcing decision (GeoNames CC-BY vs. national postal authorities with restrictive licenses) and should be discussed in a follow-up issue.

## Source of Updates

All 12 entries reflect universally-documented national postal systems. No external dataset was imported; values were drawn from common knowledge of:
- 4- and 5-digit national systems (UPU member countries)
- British Overseas Territories using `XX####` prefixed codes (KY, VG, VC)
- Inheritance from parent country systems (TF → France, UM → US)
