# Fix Summary: Foreign-zone city timezone cleanup (#1085 follow-up)

Closes the residual scope from #1085. The original issue called out a handful
of countries (ES, RO) where city timezone fields pointed at the wrong IANA zone.
Master is clean for those. This PR sweeps every remaining city row whose
timezone field belongs to a neighbouring country.

## Scope

72 rows across 4 country files:

| File | Wrong zone | Correct zone | Rows |
|------|------------|--------------|-----:|
| `contributions/cities/VN.json` | `Asia/Bangkok` | `Asia/Ho_Chi_Minh` | 63 |
| `contributions/cities/PS.json` | `Asia/Jerusalem` | `Asia/Hebron` | 6 |
| `contributions/cities/UZ.json` | `Asia/Bishkek` | `Asia/Tashkent` | 2 |
| `contributions/cities/ID.json` | `Asia/Ho_Chi_Minh` | `Asia/Pontianak` | 1 |

## Per-file rationale

- **VN (63 rows):** All 63 sit in Vietnamese provinces (state codes spanning
  northern, central, and southern VN). Vietnam observes ICT (UTC+7) in a single
  IANA zone: `Asia/Ho_Chi_Minh`. `Asia/Bangkok` is Thailand's zone — never
  correct for a Vietnamese city.

- **PS (6 rows):** All 6 sit in West Bank governates — Bethlehem (BTH),
  Hebron (HBN), Jerusalem governate (JEM), Salfit (SLT). The IANA mapping for
  the Palestinian territories is geographic: `Asia/Gaza` for Gaza Strip,
  `Asia/Hebron` for the West Bank. None of the 6 are in the Gaza Strip,
  so all map to `Asia/Hebron`. `Asia/Jerusalem` is Israel's zone.

- **UZ (2 rows):** Both are in Fergana Region (state_code `FA`), eastern
  Uzbekistan. Uzbekistan observes UZT (UTC+5) under `Asia/Tashkent` (the
  most populous IANA zone for the country) or `Asia/Samarkand`. `Asia/Bishkek`
  is Kyrgyzstan's zone — never correct for a Uzbek city.

- **ID (1 row):** Sambas (West Kalimantan, state_code `KB`) observes WIB
  (UTC+7) under `Asia/Pontianak`. `Asia/Ho_Chi_Minh` is Vietnam's zone.

## Out of scope

- **TF (Tromelin Island):** Currently tagged `Indian/Reunion`. Tromelin is
  administered by France as part of the Scattered Islands (TAAF) but is
  disputed with Mauritius. The current zone reflects de-facto administration —
  left untouched.
- **FR (Nouméa, id 160039):** Tagged `Pacific/Noumea`. State_code is `NC`
  (New Caledonia, an FR overseas collectivity). This is correct, not a bug —
  excluded from the sweep.

## Verification

```
$ python3 bin/scripts/fixes/foreign_timezone_fixes.py
Total rows fixed: 72
$ python3 bin/scripts/fixes/foreign_timezone_fixes.py
Total rows fixed: 0   # idempotent
```

After-counts: 0 VN rows tagged `Asia/Bangkok`, 0 PS rows tagged
`Asia/Jerusalem`, 0 UZ rows tagged `Asia/Bishkek`, 0 ID rows tagged
`Asia/Ho_Chi_Minh`.

Schema, cross-reference, coordinate-bounds, and duplicate validators all
pass — no FK or geometry changes, only the `timezone` text field.
