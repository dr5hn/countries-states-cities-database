# Ethiopia Missing States Fix - Summary

## Quick Reference

**Issue**: Ethiopia was missing 2 regional states  
**Status**: ✅ Fixed  
**Date**: 2025-10-14  

## What Was Added

### Sidama Regional State (ET-SI)
- Formed in 2020 from SNNPR
- Capital: Hawassa
- ~7 cities identified for future reassignment

### Southwest Ethiopia Peoples Regional State (ET-SW)
- Formed in 2021 from SNNPR
- Capital: Bonga
- ~5 cities identified for future reassignment

## Before vs After

| Metric | Before | After |
|--------|--------|-------|
| Ethiopian States | 11 | **13** ✅ |
| Regional States | 9 | **11** ✅ |
| Administrations | 2 | 2 |
| ISO Compliance | ❌ | ✅ |

## Files Changed
- `contributions/states/states.json` (added 2 entries)

## Next Steps (Future PRs)
1. Reassign ~12 cities from SNNPR to new regions once state IDs are assigned
2. Add additional cities for new regions if needed

## References
- ISO 3166-2:ET: https://www.iso.org/obp/ui#iso:code:3166:ET
- Full documentation: `.github/fixes-docs/FIX_ETHIOPIA_MISSING_STATES.md`
