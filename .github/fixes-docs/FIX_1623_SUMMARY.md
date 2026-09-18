# Fix Summary: Epitacio Huerta misclassified state + duplicated wikiDataId batch bug

## Issue Reference
**Original Issue:** [#1623](https://github.com/dr5hn/countries-states-cities-database/issues/1623) — Missed Data about City Epitacio Huerta

## Executive Summary

The issue requested adding "Epitacio Huerta" (Michoacán) as a new city, believing it was missing. It was **not** missing — `contributions/cities/MX.json` id `70312` has held this record since 2019 — but the record itself had two genuine data bugs:

1. `state_id`/`state_code` pointed to Estado de México (`3450`/`MEX`) instead of Michoacán de Ocampo (`3474`/`MIC`), the state Epitacio Huerta actually belongs to.
2. `wikiDataId` was `Q3845429`, which is not Epitacio Huerta at all — it's **Epazoyucan Municipality, Hidalgo** (verified via Wikidata: label "Epazoyucan Municipality", `P131` Hidalgo, `P625` ≈ 20.034°N 98.653°W).

Investigating the wikiDataId bug surfaced a wider batch issue: id `70312` sits in a run of 4 consecutive records (`70310`–`70313`, all `created_at: 2019-10-06`, i.e. imported in the same batch) that **all** carry the identical `wikiDataId: Q3845429`. Only the first of the four (`70310`, Epazoyucan) actually owns that ID — the next three all inherited it incorrectly, almost certainly from a copy/carry-forward bug in the original 2019 import. Each of the other three was individually verified against Wikidata (by name, state, and coordinate match) and corrected.

**This 4-record run is not an isolated incident.** An automated review of this PR (Pullfrog) flagged, and independent verification confirmed, that the same carry-forward pattern spans the entire file: **1,939 duplicate-`wikiDataId` groups covering 5,215 of `MX.json`'s 9,321 records (~3,276 records, ~35% of the file, are very likely wrong)**, with 99% of those groups being consecutive-`id` runs matching this exact shape. This PR fixes only the 4 records that motivated it — **the systemic issue is intentionally not attempted here** (each of the ~3,276 remaining records needs its own individual Wikidata verification; there's no safe bulk fix). Tracked in **[#1634](https://github.com/dr5hn/countries-states-cities-database/issues/1634)**.

## Changes Made

`contributions/cities/MX.json`:

| id | name | Field | Before | After | Verification |
|----|------|-------|--------|-------|---------------|
| 70311 | Epigmenio González | `wikiDataId` | `Q3845429` (Epazoyucan, Hidalgo) | `Q61291858` | Wikidata: "town in Pedro Escobedo Municipality, Querétaro"; coords 20°33'3"N 100°9'47"W match record's 20.55090/-100.16505 |
| 70312 | Epitacio Huerta | `state_id` | `3450` (Estado de México) | `3474` (Michoacán de Ocampo) | Real Epitacio Huerta municipality is in Michoacán, ~105km NE of Morelia |
| 70312 | Epitacio Huerta | `state_code` | `MEX` | `MIC` | matches corrected `state_id` |
| 70312 | Epitacio Huerta | `wikiDataId` | `Q3845429` (Epazoyucan, Hidalgo) | `Q49953734` | Wikidata: "municipality in the State of Michoacan"; coords 20°9'9"N 100°17'4"W match record's 20.13493/-100.29321 |
| 70313 | Ermita de Guadalupe | `wikiDataId` | `Q3845429` (Epazoyucan, Hidalgo) | `Q5835912` | Wikidata: "town in Jerez Municipality, State of Zacatecas"; coords 22°35'16"N 103°1'58"W match record's 22.58579/-103.03133 |

`70310` (Epazoyucan) — the one record in this batch that already had the correct `wikiDataId` — was left untouched.

## Verification
- Each of the 3 replacement Wikidata IDs was checked directly: label, `P17` country (Mexico), `P131` located-in administrative division, and `P625` coordinates, and each coordinate pair matches the corresponding dataset record to within measurement precision.
- JSON validated after edit (`python3 -m json.tool` / `json.load`).
- Confirmed no other record in `MX.json` still references `Q3845429` besides the correct owner (`70310`).
- Duplicate `wikiDataId` groups in `MX.json` overall: **1,939** (before and after this PR — unchanged outside the 4 records touched here). See [#1634](https://github.com/dr5hn/countries-states-cities-database/issues/1634) for the full-file scope.

## Files Changed
- `contributions/cities/MX.json` — correct 4 fields across 3 records (ids `70311`, `70312`, `70313`).
