New England municipal additions for #2066. Sources: US Census 2024 Gazetteer and TIGERweb ACS2024; 2020 Census PL 94-171 POP100. Public domain US Government work (17 USC 105). Coordinates copied unchanged from Gazetteer INTPTLAT/INTPTLONG, formatted to eight decimals. Per-record edition, retrieval time, hash, feature, population scope, identity decision and source URL: [ledger](ledgers/ne_towns_v5.jsonl). Towns and cities are level 3 under state (1) and county/planning region (2), with null city parent. Existing places and Wikidata items are preserved. New rows have no Wikidata item. CT links use the post-2022 planning regions. Census same-named CDPs/villages remain distinct.

Verified functioning municipality coverage (baseline before this PR → after additions):

| State | Added | Held | Coverage before → after |
|---|---:|---:|---|
| CT | 66 | 20 | 88/169 (52.1%) → 154/169 (91.1%) |
| MA | 54 | 23 | 280/351 (79.8%) → 334/351 (95.2%) |
| ME | 231 | 92 | 206/453 (45.5%) → 437/453 (96.5%) |
| NH | 79 | 32 | 149/234 (63.7%) → 228/234 (97.4%) |
| RI | 5 | 2 | 33/39 (84.6%) → 38/39 (97.4%) |
| VT | 175 | 27 | 54/247 (21.9%) → 229/247 (92.7%) |
| Total | 610 | 196 | 810/1493 (54.3%) → 1420/1493 (95.1%) |

Held: 73 functioning municipalities with unresolved identity/type/point and 123 other subdivisions. Review #2070 R1 adds 11 separately identified towns (CT 1, VT 10), IDs 168759–168769, following the original 599 additions (168160–168758). Each has its own Census MCD, Gazetteer point and 2020 population. Distinct contained incorporated villages/boroughs and existing CDPs remain unchanged; their presence alone does not justify holding a missing town. See the appended per-record ledger evidence.
