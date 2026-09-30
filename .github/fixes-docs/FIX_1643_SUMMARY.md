# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## Cities filed under the wrong state: 13 more countries

### How they were found
The 2019 import copied each city's population from GeoNames, so a record's source entry is the GeoNames place
(`cities500`) with the same name within 3 km and **exactly the record's population**. Per country, GeoNames'
region codes were mapped to CSC states by majority vote of the records fingerprinted to them; a record is a
candidate when its entry's code maps (at least 5 records, 80% agreement) to another state. Mexico, Spain, France
and Italy are covered by their own PRs.

256 candidates in 22 countries: Italy's 117 went to #1657. The Philippines, Sri Lanka and Sierra Leone were dropped
(GeoNames' regions are a different level from CSC's states, or predate a new province), and two records where GeoNames
predates a province split (Miraflores in Lima, La Libertad in Santa Elena). The other 86 were checked on Wikidata:
the item with the record's name within 2 km of its point, followed up its "located in" (P131) chain to a CSC state.

| Result | Records |
|---|---:|
| Wikidata agrees with GeoNames; no same-named place in the filed state; populations compatible | **20** |
| Held by a guard, moved after a hand check (Horn, Ngawi) | **2** |
| Held by a guard (a same-named place in the filed state, or a population mismatch) | 8 |
| Wikidata says the filed state is right, e.g. Yanam (Puducherry, inside Andhra Pradesh) | 15 |
| No same-named item nearby, or contained in no or several CSC states | 41 |

### Fix
**22 cities** move. Only `state_id` and `state_code` change; every record's `timezone` already fits its new state.

| Country | id | City | Was filed under | Now | Population | Wikidata | Note |
|---|---|---|---|---|---:|---|---|
| CA | 16417 | Fallingbrook | Prince Edward Island (PE) | Ontario (ON) | 25,000 | Q5432394 |  |
| CH | 17934 | Horn | St. Gallen (SG) | Thurgau (TG) | 2,274 | Q15964148, Q22640379 | Held by the guard for two hamlets named Horn in St. Gallen; the record (2,274 people) is the Thurgau municipality, by exact GeoNames population |
| DZ | 31303 | Chemini | Tizi Ouzou (15) | Béjaïa (06) | 21,585 | Q1118209, Q2962465 |  |
| DZ | 31357 | Ighram | Tizi Ouzou (15) | Béjaïa (06) | 15,030 | Q2215840 |  |
| DZ | 31372 | Makouda | Boumerdès (35) | Tizi Ouzou (15) | 34,515 | Q2374784, Q3280947 |  |
| DZ | 31456 | Tizi Gheniff | Boumerdès (35) | Tizi Ouzou (15) | 27,974 | Q3019923, Q3529984 |  |
| ET | 38625 | Dīla | Sidama (SI) | Southern Nations, Nationalities, and Peoples (SN) | 158,800 | Q905423 |  |
| GB | 49213 | Cushendall | Mid and East Antrim (MEA) | Causeway Coast and Glens (CCG) | 1,226 | Q104359932, Q2580652 | Wikidata resolves only to Northern Ireland (the district record carries another item); GeoNames and the 2015 district map say Causeway Coast and Glens |
| ID | 56886 | Ngawi | Jawa Barat (JB) | Jawa Timur (JI) | 22,412 | Q10773354, Q65299225 | Held by the guard for a population mismatch: Wikidata counts Ngawi Regency; the record is its seat town, in East Java |
| IN | 132453 | Khailar | Madhya Pradesh (MP) | Uttar Pradesh (UP) | 13,334 | Q2119908 |  |
| IN | 132934 | Margherita | Arunachal Pradesh (AR) | Assam (AS) | 26,914 | Q1924981, Q63356754 |  |
| KZ | 65657 | Būrabay | North Kazakhstan (59) | Akmola (11) | 6,500 | Q1009456 |  |
| MY | 76531 | Pantai Cenang | Perlis (09) | Kedah (02) | 15,000 | Q33328099 |  |
| NO | 79257 | Jevnaker | Innlandet (34) | Akershus (32) | 4,308 | Q11283023, Q11978556 | Akershus since the 2024 county split |
| NO | 79480 | Sande | Telemark (40) | Vestfold (39) | 1,389 | Q130348197, Q183029 | Holmestrand, Vestfold |
| RS | 97406 | Tabanović | Belgrade (00) | Mačva (08) | 1,286 | Q2736282 |  |
| RU | 98424 | Fili | Moscow (MOS) | Moscow (MOW) | 80,000 | Q1002971, Q4483851 |  |
| RU | 98425 | Filimonki | Moscow (MOS) | Moscow (MOW) | 1,329 | Q4483879 | Part of Moscow since the 2012 expansion (New Moscow) |
| RU | 99980 | Mosrentgen | Moscow (MOS) | Moscow (MOW) | 5,214 | Q4120441 | Part of Moscow since the 2012 expansion (New Moscow) |
| UA | 109819 | Kotsyubyns’ke | Kyiv (30) | Kyivska (32) | 17,623 | Q2026969 | An enclave of Kyiv Oblast inside the city of Kyiv |
| UA | 110313 | Prolisky | Kyiv (30) | Kyivska (32) | 1,852 | Q4380462 |  |
| UA | 110490 | Smyga | Khmelnytska (68) | Rivnenska (56) | 2,800 | Q2473563, Q25445118 |  |

## Rollback
Revert the commit. No `id`s change.

## Files Changed
- `contributions/cities/{CA,CH,DZ,ET,GB,ID,IN,KZ,MY,NO,RS,RU,UA}.json` — `state_id` and `state_code` on 22 records
