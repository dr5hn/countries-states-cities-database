# Fix: Saint Lucia - Remove Extra Districts

## Issue Reference
- **Issue**: [Bug]: Saint Lucia remove district
- **Issue Type**: Incorrect Data (wrong information)
- **Location**: Saint Lucia (LC)
- **Source**: [ISO 3166-2:LC](https://www.iso.org/obp/ui#iso:code:3166:LC)

## Problem
Saint Lucia had 12 districts in the database, but according to the ISO 3166-2 standard, it should have only 10 districts.

## Districts Removed
The following 2 districts were removed to align with ISO 3166-2:

1. **Praslin (LC-09)**
   - ID: 3765
   - WikiData: Q1567791
   - Note: Not listed in ISO 3166-2 standard

2. **Dauphin (LC-04)**
   - ID: 3767
   - WikiData: Q182988
   - Note: Not listed in ISO 3166-2 standard

## Correct Districts (10 total)
According to ISO 3166-2:LC, Saint Lucia has the following 10 districts:

| Type | Code | Name |
|------|------|------|
| District | LC-01 | Anse la Raye |
| District | LC-02 | Castries |
| District | LC-03 | Choiseul |
| District | LC-05 | Dennery |
| District | LC-06 | Gros Islet |
| District | LC-07 | Laborie |
| District | LC-08 | Micoud |
| District | LC-10 | Soufrière |
| District | LC-11 | Vieux Fort |
| District | LC-12 | Canaries |

## Changes Made

### Files Modified
1. **contributions/states/states.json**
   - Removed Praslin district (id: 3765, LC-09)
   - Removed Dauphin district (id: 3767, LC-04)

### Database Updates
- MySQL database updated to remove the 2 extra districts
- Total states count: 5216 → 5214 (decreased by 2)
- Saint Lucia districts: 12 → 10

### Cities Impact
- **No cities were affected**: Verified that 0 cities referenced Praslin or Dauphin districts
- All Saint Lucia cities reference the 10 correct districts

## Validation

### Before Fix
```bash
# Count of districts
$ jq '[.[] | select(.country_code == "LC")] | length' contributions/states/states.json
12
```

### After Fix
```bash
# Count of districts
$ jq '[.[] | select(.country_code == "LC")] | length' contributions/states/states.json
10

# List all districts
$ jq '[.[] | select(.country_code == "LC")] | sort_by(.iso3166_2) | .[] | {name: .name, code: .iso3166_2}'
{
  "name": "Anse la Raye",
  "code": "LC-01"
}
{
  "name": "Castries",
  "code": "LC-02"
}
{
  "name": "Choiseul",
  "code": "LC-03"
}
{
  "name": "Dennery",
  "code": "LC-05"
}
{
  "name": "Gros Islet",
  "code": "LC-06"
}
{
  "name": "Laborie",
  "code": "LC-07"
}
{
  "name": "Micoud",
  "code": "LC-08"
}
{
  "name": "Soufrière",
  "code": "LC-10"
}
{
  "name": "Vieux Fort",
  "code": "LC-11"
}
{
  "name": "Canaries",
  "code": "LC-12"
}
```

### MySQL Verification
```sql
-- Count Saint Lucia districts
SELECT COUNT(*) as count FROM states WHERE country_code = 'LC';
-- Result: 10

-- List all districts
SELECT id, name, iso3166_2 FROM states WHERE country_code = 'LC' ORDER BY name;
-- Returns exactly 10 districts matching ISO 3166-2
```

## Steps Taken

1. **Explored Repository Structure**
   - Located Saint Lucia data in `contributions/states/states.json`
   - Verified cities data in `contributions/cities/LC.json`

2. **Identified Incorrect Districts**
   - Cross-referenced with ISO 3166-2 standard
   - Found Praslin (LC-09) and Dauphin (LC-04) are not in ISO standard

3. **Verified No Cities Dependency**
   - Confirmed 0 cities reference Praslin or Dauphin districts
   - Safe to remove without affecting city data

4. **Removed Districts**
   - Created Python script to remove districts from JSON
   - Updated MySQL database directly
   - Synced MySQL back to JSON for consistency

5. **Validated Changes**
   - Verified exactly 10 districts remain
   - Confirmed all 10 districts match ISO 3166-2 standard
   - Validated district codes: LC-01, LC-02, LC-03, LC-05, LC-06, LC-07, LC-08, LC-10, LC-11, LC-12

## Source Verification
- **ISO 3166-2**: https://www.iso.org/obp/ui#iso:code:3166:LC
- **WikiData (Praslin)**: Q1567791
- **WikiData (Dauphin)**: Q182988

## Notes
- Praslin and Dauphin appear to be historical or unofficial subdivisions
- The ISO 3166-2 standard is the authoritative source for country subdivision codes
- This fix ensures the database matches international standards
