# Four decided territorial reforms for v5

These are territorial successors, with fresh state ids; no automatic redirect is allowed.
Code values below are project assignments. ISO issuance for these successor extents has not been verified.
LV-059 preserves a code string, not the identity of old state 4433.
KR-12 and EE-250 render national codes 1200000000 and 0250; AO-CBG/AO-CUB render GeoNames provider codes.

| Effective date | Retired states | New states and project codes |
| --- | --- | --- |
| 2026-07-01 | 3856 South Jeolla | 5854 Jeonnam-Gwangju Integrated Special City (KR-12) |
| 2026-07-01 | 3858 Gwangju | 5854 Jeonnam-Gwangju Integrated Special City (KR-12) |
| 2025-11-28 | 5746 Jõhvi | 5855 Jõhvi (EE-250) |
| 2025-11-28 | 5788 Toila | 5855 Jõhvi (EE-250) |
| 2025-01-01 | 226 Cuando Cubango | 5856 Cubango (AO-CBG); 5857 Cuando (AO-CUB) |
| 2025-07-01 | 4431 Varakļāni | 5858 Madona (LV-059) |
| 2025-07-01 | 4433 Madona | 5858 Madona (LV-059) |

Angola's date is administrative implementation on 1 January 2025; Law 14/24 itself commenced on publication
on 5 September 2024 and provided for gradual installation (Article 516). Latvia's amendment commenced on
30 June 2024; territorial succession followed the new council's first meeting on 1 July 2025.

All 49 reviewed city rows retain their identity fields; only the state pair changes. The 28 linked Latvian
postcodes move with the whole predecessor territories; city links, code/locality, source and point stay intact.
No counties or child-state links reference the retired states. The two Gunwi moves already landed in #2009.

New state translations are empty and Wikidata identifiers/populations are null: none is inherited from a
predecessor or seat. KR/EE/LV use named settlement anchors (GeoNames 1841811/591893/457714) within the merged
territories, not polygon centroids, extent identities or claims of a sole capital. AO uses its own ADM1 points
(13645449/13645452). See .github/licenses/SOURCES.txt for attribution.

The source/review bundle is retained in csc-data-audit: runs/specs/reforms_v5/work/. This change is bounded to
the four decided reforms; it does not certify a complete national reform audit of Angola or other countries.
