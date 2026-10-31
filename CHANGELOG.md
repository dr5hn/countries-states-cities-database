# Changelog

## v4.0 — 2026-10-09

Major release: official administrative structure for 11 countries, a new counties dataset, and six months of data
corrections ([#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643)). **Breaking changes: read
the [v4.0 release notes](https://github.com/dr5hn/countries-states-cities-database/releases/tag/v4.0) before upgrading.**

**Breaking changes:**
- New `counties` dataset (4,305: US 3,081, DE 418, PL 380, FR 333, AT 93) in every export format, and a nullable
  `cities.county_id` (29,432 cities linked). The 3,081 US counties moved from `cities` to `counties` with new ids.
- 4,486 city ids removed: 1,377 duplicates merged into the older record, the 3,081 US counties, and 28 non-places. The
  mapping is `removed_ids_v3.2_to_v4.0.csv` on the v4.0 release.
- For US, FR, IT, MX, RO, ES, DE, BR, PL, RU and AT, city `type` is a standard term (`municipality`, `city`, `town`,
  `village`, `locality`, `section`) and the new `type_local` holds the official local term. `level` is the depth in
  the official hierarchy (73,230 cities, 4,991 states).
- 7,527 cities moved to the smallest ISO 3166-2 unit that contains them, or out of a wrong state; 27 states added and
  6 retired.
- New columns `cities.type_local`, `cities.county_id` and `states.type_local`.
- Translations rebuilt for every country from Wikidata labels (109,678 cities).

**Also:** Wikidata ids corrected on 17,455 cities, names on 3,653 and coordinates on 1,457; 1,535 cities and 95 states
moved to the right time zone; 185,878 postcodes linked to their city.

## 2026-10
- **2026-10-24** - PR [#2123](https://github.com/dr5hn/countries-states-cities-database/pull/2123): Updated cities (IL) (by @dr5hn)
- **2026-10-24** - PR [#2122](https://github.com/dr5hn/countries-states-cities-database/pull/2122): Updated cities (BD) (by @dr5hn)
- **2026-10-24** - PR [#2120](https://github.com/dr5hn/countries-states-cities-database/pull/2120): Updated cities (PH) (by @dr5hn)
- **2026-10-24** - PR [#2121](https://github.com/dr5hn/countries-states-cities-database/pull/2121): Updated cities (AL, BJ, BO, CI, CN) (by @dr5hn)
- **2026-10-24** - PR [#2119](https://github.com/dr5hn/countries-states-cities-database/pull/2119): Updated cities (HU, RS, SI) (by @dr5hn)
- **2026-10-24** - PR [#2118](https://github.com/dr5hn/countries-states-cities-database/pull/2118): Updated cities (NZ) (by @dr5hn)
- **2026-10-24** - PR [#2117](https://github.com/dr5hn/countries-states-cities-database/pull/2117): Updated cities (CN, IN, IR, MX, NL) (by @dr5hn)
- **2026-10-24** - PR [#2116](https://github.com/dr5hn/countries-states-cities-database/pull/2116): Updated cities (HN, LC, PA, UY) (by @dr5hn)
- **2026-10-24** - PR [#2115](https://github.com/dr5hn/countries-states-cities-database/pull/2115): Updated cities (CN) (by @dr5hn)
- **2026-10-23** - PR [#2114](https://github.com/dr5hn/countries-states-cities-database/pull/2114): Updated cities (CN) (by @dr5hn)
- **2026-10-23** - PR [#2113](https://github.com/dr5hn/countries-states-cities-database/pull/2113): Updated cities (CN) (by @dr5hn)
- **2026-10-23** - PR [#2112](https://github.com/dr5hn/countries-states-cities-database/pull/2112): Updated cities (GT) (by @dr5hn)
- **2026-10-23** - PR [#2111](https://github.com/dr5hn/countries-states-cities-database/pull/2111): Updated cities (IT) (by @dr5hn)
- **2026-10-23** - PR [#2110](https://github.com/dr5hn/countries-states-cities-database/pull/2110): Updated cities (UA) (by @dr5hn)
- **2026-10-23** - PR [#2109](https://github.com/dr5hn/countries-states-cities-database/pull/2109): Updated cities (IT, TW) (by @dr5hn)
- **2026-10-23** - PR [#2105](https://github.com/dr5hn/countries-states-cities-database/pull/2105): Updated cities (LV) (by @dr5hn)
- **2026-10-22** - PR [#2104](https://github.com/dr5hn/countries-states-cities-database/pull/2104): Updated cities (BE, IE, IS, LU, NO) (by @dr5hn)
- **2026-10-21** - PR [#2102](https://github.com/dr5hn/countries-states-cities-database/pull/2102): Updated cities (PT) (by @dr5hn)
- **2026-10-21** - PR [#2101](https://github.com/dr5hn/countries-states-cities-database/pull/2101): Updated cities (AU) (by @dr5hn)
- **2026-10-21** - PR [#2100](https://github.com/dr5hn/countries-states-cities-database/pull/2100): Updated cities (UA) (by @dr5hn)
- **2026-10-21** - PR [#2099](https://github.com/dr5hn/countries-states-cities-database/pull/2099): Updated cities (CA, DE, MX) (by @dr5hn)
- **2026-10-21** - PR [#2098](https://github.com/dr5hn/countries-states-cities-database/pull/2098): Updated cities (ES, FR, IT) (by @dr5hn)
- **2026-10-20** - PR [#2097](https://github.com/dr5hn/countries-states-cities-database/pull/2097): Updated cities (IN) (by @dr5hn)
- **2026-10-20** - PR [#2096](https://github.com/dr5hn/countries-states-cities-database/pull/2096): Updated cities (AU) (by @dr5hn)
- **2026-10-20** - PR [#2095](https://github.com/dr5hn/countries-states-cities-database/pull/2095): Updated cities (US) (by @dr5hn)
- **2026-10-20** - PR [#2094](https://github.com/dr5hn/countries-states-cities-database/pull/2094): Updated cities (CZ) (by @dr5hn)
- **2026-10-20** - PR [#2093](https://github.com/dr5hn/countries-states-cities-database/pull/2093): Updated cities (FR, US) (by @dr5hn)
- **2026-10-20** - PR [#2092](https://github.com/dr5hn/countries-states-cities-database/pull/2092): Updated cities (HR) (by @dr5hn)
- **2026-10-20** - PR [#2091](https://github.com/dr5hn/countries-states-cities-database/pull/2091): Updated cities (JP) (by @dr5hn)
- **2026-10-20** - PR [#2090](https://github.com/dr5hn/countries-states-cities-database/pull/2090): Updated cities (PL) (by @dr5hn)
- **2026-10-20** - PR [#2089](https://github.com/dr5hn/countries-states-cities-database/pull/2089): Updated cities (US) (by @dr5hn)
- **2026-10-20** - PR [#2088](https://github.com/dr5hn/countries-states-cities-database/pull/2088): Updated cities (FR, JP) (by @dr5hn)
- **2026-10-20** - PR [#2087](https://github.com/dr5hn/countries-states-cities-database/pull/2087): Updated cities (PT) (by @dr5hn)
- **2026-10-20** - PR [#2086](https://github.com/dr5hn/countries-states-cities-database/pull/2086): Updated cities (IN) (by @dr5hn)
- **2026-10-20** - PR [#2085](https://github.com/dr5hn/countries-states-cities-database/pull/2085): Updated cities (DE) (by @dr5hn)
- **2026-10-20** - PR [#2084](https://github.com/dr5hn/countries-states-cities-database/pull/2084): Updated cities (ES) (by @dr5hn)
- **2026-10-20** - PR [#2083](https://github.com/dr5hn/countries-states-cities-database/pull/2083): Updated cities (PL) (by @dr5hn)
- **2026-10-20** - PR [#2082](https://github.com/dr5hn/countries-states-cities-database/pull/2082): Updated cities (AT) (by @dr5hn)
- **2026-10-20** - PR [#2081](https://github.com/dr5hn/countries-states-cities-database/pull/2081): Updated cities (MX) (by @dr5hn)
- **2026-10-20** - PR [#2080](https://github.com/dr5hn/countries-states-cities-database/pull/2080): Updated cities (CA) (by @dr5hn)
- **2026-10-20** - PR [#2079](https://github.com/dr5hn/countries-states-cities-database/pull/2079): Updated cities (GB) (by @dr5hn)
- **2026-10-19** - PR [#2078](https://github.com/dr5hn/countries-states-cities-database/pull/2078): Updated cities (AU) (by @dr5hn)
- **2026-10-19** - PR [#2077](https://github.com/dr5hn/countries-states-cities-database/pull/2077): Updated states (by @dr5hn)
- **2026-10-19** - PR [#2075](https://github.com/dr5hn/countries-states-cities-database/pull/2075): Updated cities (US) (by @dr5hn)
- **2026-10-19** - PR [#2076](https://github.com/dr5hn/countries-states-cities-database/pull/2076): Updated cities (UY) (by @dr5hn)
- **2026-10-19** - PR [#2072](https://github.com/dr5hn/countries-states-cities-database/pull/2072): Updated cities, Updated states (AR, CH, CN, DE, EE) (by @github-actions[bot])
- **2026-10-19** - PR [#2070](https://github.com/dr5hn/countries-states-cities-database/pull/2070): Updated cities (US) (by @dr5hn)
- **2026-10-19** - PR [#2069](https://github.com/dr5hn/countries-states-cities-database/pull/2069): Updated cities (US) (by @dr5hn)
- **2026-10-16** - PR [#2062](https://github.com/dr5hn/countries-states-cities-database/pull/2062): Updated countries (by @dr5hn)
- **2026-10-16** - PR [#2061](https://github.com/dr5hn/countries-states-cities-database/pull/2061): Updated countries (by @dr5hn)
- **2026-10-16** - PR [#2060](https://github.com/dr5hn/countries-states-cities-database/pull/2060): Updated cities, Updated states (AO, EE, KR, LV) (by @dr5hn)
- **2026-10-16** - PR [#2057](https://github.com/dr5hn/countries-states-cities-database/pull/2057): Added cities, Updated cities (CN, DZ, EH, KZ, MA) (by @dr5hn)
- **2026-10-15** - PR [#2047](https://github.com/dr5hn/countries-states-cities-database/pull/2047): Updated cities (AR, CH, CN, DE, EE) (by @dr5hn)
- **2026-10-15** - PR [#2045](https://github.com/dr5hn/countries-states-cities-database/pull/2045): Updated cities (AR, AU, BE, BG, BR) (by @dr5hn)
- **2026-10-15** - PR [#2042](https://github.com/dr5hn/countries-states-cities-database/pull/2042): Updated cities (AR, GB, ID, IN, NZ) (by @dr5hn)
- **2026-10-15** - PR [#2041](https://github.com/dr5hn/countries-states-cities-database/pull/2041): Updated cities (AM, AR, AT, AU, BG) (by @dr5hn)
- **2026-10-14** - PR [#2035](https://github.com/dr5hn/countries-states-cities-database/pull/2035): Updated countries (by @dr5hn)
- **2026-10-14** - PR [#2027](https://github.com/dr5hn/countries-states-cities-database/pull/2027): Updated cities (RO) (by @vicuts)
- **2026-10-14** - PR [#2033](https://github.com/dr5hn/countries-states-cities-database/pull/2033): Updated cities (RO) (by @dr5hn)
- **2026-10-14** - PR [#2025](https://github.com/dr5hn/countries-states-cities-database/pull/2025): Updated cities (NZ) (by @dr5hn)
- **2026-10-14** - PR [#2032](https://github.com/dr5hn/countries-states-cities-database/pull/2032): Updated cities, Updated states, Updated countries (FR, GB, KE) (by @dr5hn)
- **2026-10-14** - PR [#2030](https://github.com/dr5hn/countries-states-cities-database/pull/2030): Updated cities (RO) (by @dr5hn)
- **2026-10-13** - PR [#2022](https://github.com/dr5hn/countries-states-cities-database/pull/2022): Updated cities (DZ, KZ, TZ) (by @dr5hn)
- **2026-10-13** - PR [#2019](https://github.com/dr5hn/countries-states-cities-database/pull/2019): Updated states (by @dr5hn)
- **2026-10-13** - PR [#2020](https://github.com/dr5hn/countries-states-cities-database/pull/2020): Updated states (by @dr5hn)
- **2026-10-13** - PR [#2015](https://github.com/dr5hn/countries-states-cities-database/pull/2015): Updated states (by @dr5hn)
- **2026-10-13** - PR [#2013](https://github.com/dr5hn/countries-states-cities-database/pull/2013): Updated cities (AM, BY, ZA) (by @dr5hn)
- **2026-10-13** - PR [#2012](https://github.com/dr5hn/countries-states-cities-database/pull/2012): Updated cities (IL, PS, UA) (by @dr5hn)
- **2026-10-13** - PR [#2009](https://github.com/dr5hn/countries-states-cities-database/pull/2009): Updated cities, Updated states, Updated countries (KR, MA, PS, RU, UA) (by @dr5hn)
- **2026-10-13** - PR [#2008](https://github.com/dr5hn/countries-states-cities-database/pull/2008): Updated cities (CL, KR) (by @dr5hn)
- **2026-10-13** - PR [#2007](https://github.com/dr5hn/countries-states-cities-database/pull/2007): Updated cities (EE, IE) (by @dr5hn)
- **2026-10-13** - PR [#2005](https://github.com/dr5hn/countries-states-cities-database/pull/2005): Updated cities (AF, AL, AM, AO, AZ) (by @dr5hn)
- **2026-10-13** - PR [#2006](https://github.com/dr5hn/countries-states-cities-database/pull/2006): Updated cities (IE, LU, NZ) (by @dr5hn)
- **2026-10-13** - PR [#2004](https://github.com/dr5hn/countries-states-cities-database/pull/2004): Updated cities (EE, SI, SK) (by @dr5hn)
- **2026-10-13** - PR [#2003](https://github.com/dr5hn/countries-states-cities-database/pull/2003): Updated cities (CN) (by @dr5hn)
- **2026-10-13** - PR [#2002](https://github.com/dr5hn/countries-states-cities-database/pull/2002): Updated cities (ID) (by @dr5hn)
- **2026-10-13** - PR [#2001](https://github.com/dr5hn/countries-states-cities-database/pull/2001): Updated cities (CN) (by @dr5hn)
- **2026-10-13** - PR [#2000](https://github.com/dr5hn/countries-states-cities-database/pull/2000): Updated cities (CN) (by @dr5hn)
- **2026-10-13** - PR [#1999](https://github.com/dr5hn/countries-states-cities-database/pull/1999): Updated cities (CN) (by @dr5hn)
- **2026-10-13** - PR [#1998](https://github.com/dr5hn/countries-states-cities-database/pull/1998): Updated cities (CN) (by @dr5hn)
- **2026-10-13** - PR [#1997](https://github.com/dr5hn/countries-states-cities-database/pull/1997): Updated cities (CN) (by @dr5hn)
- **2026-10-13** - PR [#1996](https://github.com/dr5hn/countries-states-cities-database/pull/1996): Updated cities (CN) (by @dr5hn)
- **2026-10-13** - PR [#1995](https://github.com/dr5hn/countries-states-cities-database/pull/1995): Updated cities (CN) (by @dr5hn)
- **2026-10-13** - PR [#1994](https://github.com/dr5hn/countries-states-cities-database/pull/1994): Updated cities (CN) (by @dr5hn)
- **2026-10-13** - PR [#1993](https://github.com/dr5hn/countries-states-cities-database/pull/1993): Updated cities (CN) (by @dr5hn)
- **2026-10-12** - PR [#1992](https://github.com/dr5hn/countries-states-cities-database/pull/1992): Updated cities (CN) (by @dr5hn)
- **2026-10-12** - PR [#1990](https://github.com/dr5hn/countries-states-cities-database/pull/1990): Updated cities (CN) (by @dr5hn)
- **2026-10-12** - PR [#1989](https://github.com/dr5hn/countries-states-cities-database/pull/1989): Updated cities (VN) (by @dr5hn)
- **2026-10-12** - PR [#1987](https://github.com/dr5hn/countries-states-cities-database/pull/1987): Updated cities (CN) (by @dr5hn)
- **2026-10-12** - PR [#1988](https://github.com/dr5hn/countries-states-cities-database/pull/1988): Updated cities (TR) (by @dr5hn)
- **2026-10-12** - PR [#1986](https://github.com/dr5hn/countries-states-cities-database/pull/1986): Updated cities (CN) (by @dr5hn)
- **2026-10-12** - PR [#1985](https://github.com/dr5hn/countries-states-cities-database/pull/1985): Updated cities (IN) (by @dr5hn)
- **2026-10-12** - PR [#1981](https://github.com/dr5hn/countries-states-cities-database/pull/1981): Updated cities (IN) (by @dr5hn)
- **2026-10-12** - PR [#1984](https://github.com/dr5hn/countries-states-cities-database/pull/1984): Updated cities (CN) (by @dr5hn)
- **2026-10-12** - PR [#1983](https://github.com/dr5hn/countries-states-cities-database/pull/1983): Updated cities (IN) (by @dr5hn)
- **2026-10-12** - PR [#1982](https://github.com/dr5hn/countries-states-cities-database/pull/1982): Updated cities (CN) (by @dr5hn)
- **2026-10-12** - PR [#1980](https://github.com/dr5hn/countries-states-cities-database/pull/1980): Updated cities (IN, US) (by @dr5hn)
- **2026-10-12** - PR [#1979](https://github.com/dr5hn/countries-states-cities-database/pull/1979): Updated cities (CN) (by @dr5hn)
- **2026-10-12** - PR [#1978](https://github.com/dr5hn/countries-states-cities-database/pull/1978): Updated cities (NL) (by @dr5hn)
- **2026-10-12** - PR [#1977](https://github.com/dr5hn/countries-states-cities-database/pull/1977): Updated cities (VN) (by @dr5hn)
- **2026-10-12** - PR [#1975](https://github.com/dr5hn/countries-states-cities-database/pull/1975): Updated cities (CN) (by @dr5hn)
- **2026-10-12** - PR [#1972](https://github.com/dr5hn/countries-states-cities-database/pull/1972): Updated cities (IN) (by @dr5hn)
- **2026-10-12** - PR [#1971](https://github.com/dr5hn/countries-states-cities-database/pull/1971): Updated cities (GB) (by @dr5hn)
- **2026-10-12** - PR [#1969](https://github.com/dr5hn/countries-states-cities-database/pull/1969): Updated cities (AR, PE) (by @dr5hn)
- **2026-10-12** - PR [#1967](https://github.com/dr5hn/countries-states-cities-database/pull/1967): Updated cities (US) (by @dr5hn)
- **2026-10-12** - PR [#1966](https://github.com/dr5hn/countries-states-cities-database/pull/1966): Updated cities (AU, MX, PH) (by @dr5hn)
- **2026-10-12** - PR [#1965](https://github.com/dr5hn/countries-states-cities-database/pull/1965): Updated cities (AU) (by @dr5hn)
- **2026-10-12** - PR [#1964](https://github.com/dr5hn/countries-states-cities-database/pull/1964): Updated cities (BR, MX) (by @dr5hn)
- **2026-10-12** - PR [#1963](https://github.com/dr5hn/countries-states-cities-database/pull/1963): Updated cities (MX) (by @dr5hn)
- **2026-10-12** - PR [#1962](https://github.com/dr5hn/countries-states-cities-database/pull/1962): Updated cities (BR) (by @dr5hn)
- **2026-10-12** - PR [#1961](https://github.com/dr5hn/countries-states-cities-database/pull/1961): Updated cities (PH) (by @dr5hn)
- **2026-10-12** - PR [#1959](https://github.com/dr5hn/countries-states-cities-database/pull/1959): Updated cities (AR) (by @dr5hn)
- **2026-10-12** - PR [#1958](https://github.com/dr5hn/countries-states-cities-database/pull/1958): Updated cities (NG) (by @dr5hn)
- **2026-10-12** - PR [#1957](https://github.com/dr5hn/countries-states-cities-database/pull/1957): Updated cities (HN) (by @dr5hn)
- **2026-10-12** - PR [#1956](https://github.com/dr5hn/countries-states-cities-database/pull/1956): Updated cities (PA) (by @dr5hn)
- **2026-10-12** - PR [#1952](https://github.com/dr5hn/countries-states-cities-database/pull/1952): Updated cities (AO, DE, IN) (by @dr5hn)
- **2026-10-12** - PR [#1955](https://github.com/dr5hn/countries-states-cities-database/pull/1955): Updated cities (ID) (by @dr5hn)
- **2026-10-12** - PR [#1954](https://github.com/dr5hn/countries-states-cities-database/pull/1954): Updated cities (GB) (by @dr5hn)
- **2026-10-12** - PR [#1953](https://github.com/dr5hn/countries-states-cities-database/pull/1953): Updated cities (JM) (by @dr5hn)
- **2026-10-11** - PR [#1951](https://github.com/dr5hn/countries-states-cities-database/pull/1951): Updated cities (AT, GR, IN, IT, PH) (by @dr5hn)
- **2026-10-11** - PR [#1949](https://github.com/dr5hn/countries-states-cities-database/pull/1949): Updated cities (GR) (by @dr5hn)
- **2026-10-11** - PR [#1948](https://github.com/dr5hn/countries-states-cities-database/pull/1948): Updated cities (IT, MC) (by @dr5hn)
- **2026-10-11** - PR [#1947](https://github.com/dr5hn/countries-states-cities-database/pull/1947): Updated cities (NL) (by @dr5hn)
- **2026-10-11** - PR [#1944](https://github.com/dr5hn/countries-states-cities-database/pull/1944): Updated cities (AT, AU) (by @dr5hn)
- **2026-10-11** - PR [#1946](https://github.com/dr5hn/countries-states-cities-database/pull/1946): Updated cities (IT, PT, VN) (by @github-actions[bot])
- **2026-10-11** - PR [#1945](https://github.com/dr5hn/countries-states-cities-database/pull/1945): Updated cities (PT) (by @dr5hn)
- **2026-10-11** - PR [#1943](https://github.com/dr5hn/countries-states-cities-database/pull/1943): Updated cities (PT) (by @dr5hn)
- **2026-10-11** - PR [#1941](https://github.com/dr5hn/countries-states-cities-database/pull/1941): Updated cities (RU, TR, VN) (by @dr5hn)
- **2026-10-11** - PR [#1942](https://github.com/dr5hn/countries-states-cities-database/pull/1942): Updated cities (HK, RU, TF, UA) (by @dr5hn)
- **2026-10-11** - PR [#1940](https://github.com/dr5hn/countries-states-cities-database/pull/1940): Updated cities (RU) (by @dr5hn)
- **2026-10-11** - PR [#1939](https://github.com/dr5hn/countries-states-cities-database/pull/1939): Updated cities (VN) (by @dr5hn)
- **2026-10-11** - PR [#1938](https://github.com/dr5hn/countries-states-cities-database/pull/1938): Updated cities (LC) (by @dr5hn)
- **2026-10-11** - PR [#1937](https://github.com/dr5hn/countries-states-cities-database/pull/1937): Updated cities (SA) (by @dr5hn)
- **2026-10-11** - PR [#1936](https://github.com/dr5hn/countries-states-cities-database/pull/1936): Updated cities (PK) (by @dr5hn)
- **2026-10-11** - PR [#1935](https://github.com/dr5hn/countries-states-cities-database/pull/1935): Updated cities (TW) (by @dr5hn)
- **2026-10-11** - PR [#1934](https://github.com/dr5hn/countries-states-cities-database/pull/1934): Updated cities (IT) (by @dr5hn)
- **2026-10-11** - PR [#1932](https://github.com/dr5hn/countries-states-cities-database/pull/1932): Updated cities (ES, FR, IN, MX, PH) (by @dr5hn)
- **2026-10-11** - PR [#1933](https://github.com/dr5hn/countries-states-cities-database/pull/1933): Updated cities (RU, TR) (by @dr5hn)
- **2026-10-11** - PR [#1931](https://github.com/dr5hn/countries-states-cities-database/pull/1931): Updated cities (IT) (by @dr5hn)
- **2026-10-11** - PR [#1930](https://github.com/dr5hn/countries-states-cities-database/pull/1930): Updated cities (FR) (by @dr5hn)
- **2026-10-11** - PR [#1929](https://github.com/dr5hn/countries-states-cities-database/pull/1929): Updated cities (ES) (by @dr5hn)
- **2026-10-11** - PR [#1928](https://github.com/dr5hn/countries-states-cities-database/pull/1928): Updated cities (PH) (by @dr5hn)
- **2026-10-11** - PR [#1927](https://github.com/dr5hn/countries-states-cities-database/pull/1927): Updated cities (AU, BE, CA, DK, FI) (by @dr5hn)
- **2026-10-11** - PR [#1926](https://github.com/dr5hn/countries-states-cities-database/pull/1926): Updated cities (TH) (by @dr5hn)
- **2026-10-11** - PR [#1925](https://github.com/dr5hn/countries-states-cities-database/pull/1925): Updated cities (MX) (by @dr5hn)
- **2026-10-11** - PR [#1924](https://github.com/dr5hn/countries-states-cities-database/pull/1924): Updated cities (AF, AG, BD, ET, FJ) (by @github-actions[bot])
- **2026-10-11** - PR [#1923](https://github.com/dr5hn/countries-states-cities-database/pull/1923): Updated cities (GB) (by @dr5hn)
- **2026-10-11** - PR [#1921](https://github.com/dr5hn/countries-states-cities-database/pull/1921): Updated cities (RU) (by @dr5hn)
- **2026-10-11** - PR [#1922](https://github.com/dr5hn/countries-states-cities-database/pull/1922): Updated cities (AT, CH, CZ, MX, NL) (by @dr5hn)
- **2026-10-11** - PR [#1920](https://github.com/dr5hn/countries-states-cities-database/pull/1920): Updated cities (AT, ES, JP, PH, PT) (by @dr5hn)
- **2026-10-11** - PR [#1919](https://github.com/dr5hn/countries-states-cities-database/pull/1919): Updated cities (GB) (by @dr5hn)
- **2026-10-11** - PR [#1918](https://github.com/dr5hn/countries-states-cities-database/pull/1918): Updated cities (US) (by @dr5hn)
- **2026-10-11** - PR [#1917](https://github.com/dr5hn/countries-states-cities-database/pull/1917): Updated cities (RU) (by @dr5hn)
- **2026-10-11** - PR [#1916](https://github.com/dr5hn/countries-states-cities-database/pull/1916): Updated cities (UY) (by @dr5hn)
- **2026-10-11** - PR [#1914](https://github.com/dr5hn/countries-states-cities-database/pull/1914): Updated cities (ID) (by @dr5hn)
- **2026-10-11** - PR [#1915](https://github.com/dr5hn/countries-states-cities-database/pull/1915): Updated cities (RU) (by @dr5hn)
- **2026-10-11** - PR [#1913](https://github.com/dr5hn/countries-states-cities-database/pull/1913): Updated cities (BR, DE, ES, FR, IT) (by @dr5hn)
- **2026-10-11** - PR [#1912](https://github.com/dr5hn/countries-states-cities-database/pull/1912): Updated cities (PH) (by @dr5hn)
- **2026-10-11** - PR [#1910](https://github.com/dr5hn/countries-states-cities-database/pull/1910): Updated cities (AF, AG, BD, ET, FJ) (by @dr5hn)
- **2026-10-11** - PR [#1911](https://github.com/dr5hn/countries-states-cities-database/pull/1911): Updated cities (US) (by @dr5hn)
- **2026-10-11** - PR [#1909](https://github.com/dr5hn/countries-states-cities-database/pull/1909): Updated cities (GT) (by @dr5hn)
- **2026-10-11** - PR [#1907](https://github.com/dr5hn/countries-states-cities-database/pull/1907): Updated cities (AR, PE, TH) (by @dr5hn)
- **2026-10-11** - PR [#1908](https://github.com/dr5hn/countries-states-cities-database/pull/1908): Updated cities (RS) (by @dr5hn)
- **2026-10-11** - PR [#1906](https://github.com/dr5hn/countries-states-cities-database/pull/1906): Updated cities (JM, NG) (by @dr5hn)
- **2026-10-11** - PR [#1904](https://github.com/dr5hn/countries-states-cities-database/pull/1904): Updated cities (MD, RO) (by @vicuts)
- **2026-10-10** - PR [#1901](https://github.com/dr5hn/countries-states-cities-database/pull/1901): Updated cities (PE) (by @dr5hn)
- **2026-10-10** - PR [#1899](https://github.com/dr5hn/countries-states-cities-database/pull/1899): Updated cities (FI) (by @dr5hn)
- **2026-10-10** - PR [#1894](https://github.com/dr5hn/countries-states-cities-database/pull/1894): Updated cities (DK) (by @dr5hn)
- **2026-10-10** - PR [#1890](https://github.com/dr5hn/countries-states-cities-database/pull/1890): Updated cities (NG) (by @dr5hn)
- **2026-10-10** - PR [#1893](https://github.com/dr5hn/countries-states-cities-database/pull/1893): Updated cities (HR) (by @dr5hn)
- **2026-10-10** - PR [#1892](https://github.com/dr5hn/countries-states-cities-database/pull/1892): Updated cities (BG) (by @dr5hn)
- **2026-10-10** - PR [#1888](https://github.com/dr5hn/countries-states-cities-database/pull/1888): Updated cities (JM) (by @dr5hn)
- **2026-10-10** - PR [#1886](https://github.com/dr5hn/countries-states-cities-database/pull/1886): Updated cities (HR) (by @dr5hn)
- **2026-10-10** - PR [#1884](https://github.com/dr5hn/countries-states-cities-database/pull/1884): Updated cities (HN) (by @dr5hn)
- **2026-10-10** - PR [#1883](https://github.com/dr5hn/countries-states-cities-database/pull/1883): Updated cities (DE) (by @dr5hn)
- **2026-10-10** - PR [#1881](https://github.com/dr5hn/countries-states-cities-database/pull/1881): Updated cities (PA) (by @dr5hn)
- **2026-10-10** - PR [#1879](https://github.com/dr5hn/countries-states-cities-database/pull/1879): Updated cities (UY) (by @dr5hn)
- **2026-10-10** - PR [#1877](https://github.com/dr5hn/countries-states-cities-database/pull/1877): Updated cities (HR) (by @dr5hn)
- **2026-10-10** - PR [#1878](https://github.com/dr5hn/countries-states-cities-database/pull/1878): Updated cities (BE, NO, TR) (by @dr5hn)
- **2026-10-10** - PR [#1873](https://github.com/dr5hn/countries-states-cities-database/pull/1873): Updated cities (HR) (by @dr5hn)
- **2026-10-10** - PR [#1871](https://github.com/dr5hn/countries-states-cities-database/pull/1871): Updated cities (DE) (by @dr5hn)
- **2026-10-10** - PR [#1872](https://github.com/dr5hn/countries-states-cities-database/pull/1872): Updated cities (BE, GB, NO, TR) (by @dr5hn)
- **2026-10-10** - PR [#1867](https://github.com/dr5hn/countries-states-cities-database/pull/1867): Updated cities (BE) (by @dr5hn)
- **2026-10-10** - PR [#1866](https://github.com/dr5hn/countries-states-cities-database/pull/1866): Updated cities (CA) (by @dr5hn)
- **2026-10-10** - PR [#1865](https://github.com/dr5hn/countries-states-cities-database/pull/1865): Updated cities (TR) (by @dr5hn)
- **2026-10-10** - PR [#1861](https://github.com/dr5hn/countries-states-cities-database/pull/1861): Updated cities (NO) (by @dr5hn)
- **2026-10-10** - PR [#1860](https://github.com/dr5hn/countries-states-cities-database/pull/1860): Updated cities (BE) (by @dr5hn)
- **2026-10-10** - PR [#1859](https://github.com/dr5hn/countries-states-cities-database/pull/1859): Updated cities (SE) (by @dr5hn)
- **2026-10-01** - PR [#1671](https://github.com/dr5hn/countries-states-cities-database/pull/1671): Updated cities (MX) (by @dr5hn)
- **2026-10-01** - PR [#1675](https://github.com/dr5hn/countries-states-cities-database/pull/1675): Updated cities (IN, MX, PH, PT) (by @dr5hn)
- **2026-10-01** - PR [#1669](https://github.com/dr5hn/countries-states-cities-database/pull/1669): Updated cities (CN) (by @dr5hn)
- **2026-10-01** - PR [#1661](https://github.com/dr5hn/countries-states-cities-database/pull/1661): Updated cities (GB, GR, IN, MX, NO) (by @dr5hn)
- **2026-10-01** - PR [#1667](https://github.com/dr5hn/countries-states-cities-database/pull/1667): Updated cities, Updated states (AU, BR, CA, CD, FM) (by @dr5hn)
- **2026-10-01** - PR [#1673](https://github.com/dr5hn/countries-states-cities-database/pull/1673): Updated countries (by @dr5hn)
- **2026-10-01** - PR [#1672](https://github.com/dr5hn/countries-states-cities-database/pull/1672): Updated countries (by @dr5hn)
- **2026-10-01** - PR [#1670](https://github.com/dr5hn/countries-states-cities-database/pull/1670): Updated cities (FR, GB) (by @dr5hn)
- **2026-10-01** - PR [#1668](https://github.com/dr5hn/countries-states-cities-database/pull/1668): Updated states (by @dr5hn)
- **2026-10-01** - PR [#1665](https://github.com/dr5hn/countries-states-cities-database/pull/1665): Updated cities (PH) (by @dr5hn)
- **2026-10-01** - PR [#1664](https://github.com/dr5hn/countries-states-cities-database/pull/1664): Updated cities (PH) (by @dr5hn)
- **2026-10-01** - PR [#1663](https://github.com/dr5hn/countries-states-cities-database/pull/1663): Updated cities (PH) (by @dr5hn)
- **2026-10-01** - PR [#1662](https://github.com/dr5hn/countries-states-cities-database/pull/1662): Updated states (by @dr5hn)
- **2026-10-01** - PR [#1658](https://github.com/dr5hn/countries-states-cities-database/pull/1658): Updated cities (CA, CH, DZ, GB, ID) (by @dr5hn)
- **2026-10-01** - PR [#1642](https://github.com/dr5hn/countries-states-cities-database/pull/1642): Updated cities (FR) (by @dr5hn)
- **2026-10-01** - PR [#1660](https://github.com/dr5hn/countries-states-cities-database/pull/1660): Updated cities (JP, PT, UA) (by @dr5hn)
- **2026-10-01** - PR [#1656](https://github.com/dr5hn/countries-states-cities-database/pull/1656): Updated cities (ES) (by @dr5hn)
- **2026-10-01** - PR [#1649](https://github.com/dr5hn/countries-states-cities-database/pull/1649): Updated cities (AU, CA, ID, KI, MX) (by @dr5hn)
- **2026-10-01** - PR [#1666](https://github.com/dr5hn/countries-states-cities-database/pull/1666): Updated countries (by @dr5hn)
- **2026-10-01** - PR [#1657](https://github.com/dr5hn/countries-states-cities-database/pull/1657): Updated cities (IT) (by @dr5hn)
- **2026-10-01** - PR [#1655](https://github.com/dr5hn/countries-states-cities-database/pull/1655): Updated cities (MX) (by @dr5hn)
- **2026-10-01** - PR [#1654](https://github.com/dr5hn/countries-states-cities-database/pull/1654): Updated cities (FR) (by @dr5hn)
- **2026-10-01** - PR [#1652](https://github.com/dr5hn/countries-states-cities-database/pull/1652): Updated cities (MX) (by @dr5hn)
- **2026-10-01** - PR [#1647](https://github.com/dr5hn/countries-states-cities-database/pull/1647): Updated cities (AM, CN, CY, ES, FR) (by @dr5hn)
- **2026-10-01** - PR [#1659](https://github.com/dr5hn/countries-states-cities-database/pull/1659): Updated states (by @dr5hn)
- **2026-10-01** - PR [#1653](https://github.com/dr5hn/countries-states-cities-database/pull/1653): Updated states (by @dr5hn)
- **2026-10-01** - PR [#1646](https://github.com/dr5hn/countries-states-cities-database/pull/1646): Updated states (by @dr5hn)
- **2026-10-01** - PR [#1648](https://github.com/dr5hn/countries-states-cities-database/pull/1648): Updated cities (CL, FR) (by @dr5hn)
- **2026-10-01** - PR [#1644](https://github.com/dr5hn/countries-states-cities-database/pull/1644): Updated cities (PR) (by @dr5hn)

## 2026-09
- **2026-09-28** - PR [#1640](https://github.com/dr5hn/countries-states-cities-database/pull/1640): Updated cities (AE, CU, DE, GB, TW) (by @github-actions[bot])
- **2026-09-28** - PR [#1637](https://github.com/dr5hn/countries-states-cities-database/pull/1637): Updated cities (MX) (by @dr5hn)
- **2026-09-28** - PR [#1638](https://github.com/dr5hn/countries-states-cities-database/pull/1638): Updated cities (US) (by @dr5hn)
- **2026-09-26** - PR [#1636](https://github.com/dr5hn/countries-states-cities-database/pull/1636): Updated cities (IN) (by @dr5hn)
- **2026-09-26** - PR [#1635](https://github.com/dr5hn/countries-states-cities-database/pull/1635): Updated cities, Updated states (TW) (by @joepspsps2)
- **2026-09-26** - PR [#1632](https://github.com/dr5hn/countries-states-cities-database/pull/1632): Updated cities (DE) (by @rahulpawar-31)
- **2026-09-26** - PR [#1631](https://github.com/dr5hn/countries-states-cities-database/pull/1631): Updated cities (DE) (by @rahulpawar-31)
- **2026-09-26** - PR [#1630](https://github.com/dr5hn/countries-states-cities-database/pull/1630): Updated cities (MX) (by @rahulpawar-31)
- **2026-09-26** - PR [#1629](https://github.com/dr5hn/countries-states-cities-database/pull/1629): Updated cities (IN) (by @rahulpawar-31)
- **2026-09-26** - PR [#1628](https://github.com/dr5hn/countries-states-cities-database/pull/1628): Updated countries (by @rahulpawar-31)
- **2026-09-26** - PR [#1625](https://github.com/dr5hn/countries-states-cities-database/pull/1625): Updated cities (DK) (by @ebarped)

## 2026-08
- **2026-08-25** - PR [#1586](https://github.com/dr5hn/countries-states-cities-database/pull/1586): Updated cities (AE) (by @NailNilo)
- **2026-08-08** - PR [#1611](https://github.com/dr5hn/countries-states-cities-database/pull/1611): Updated cities (CU) (by @dr5hn)
- **2026-08-08** - PR [#1600](https://github.com/dr5hn/countries-states-cities-database/pull/1600): Updated cities (GB) (by @suryatejaKONDLA)
- **2026-08-08** - PR [#1609](https://github.com/dr5hn/countries-states-cities-database/pull/1609): Updated countries (by @cl3mcg)
- **2026-08-08** - PR [#1608](https://github.com/dr5hn/countries-states-cities-database/pull/1608): Updated states (by @fdeveli-cb)
- **2026-07-29** - PR [#1602](https://github.com/dr5hn/countries-states-cities-database/pull/1602): Updated cities (BE) (by @dr5hn)

## 2026-07
- **2026-07-11** - PR [#1598](https://github.com/dr5hn/countries-states-cities-database/pull/1598): Updated cities, Updated countries (NZ, US) (by @github-actions[bot])
- **2026-07-11** - PR [#1597](https://github.com/dr5hn/countries-states-cities-database/pull/1597): Updated cities (IR) (by @dr5hn)
- **2026-07-11** - PR [#1595](https://github.com/dr5hn/countries-states-cities-database/pull/1595): Updated cities (NZ) (by @dr5hn)
- **2026-07-11** - PR [#1593](https://github.com/dr5hn/countries-states-cities-database/pull/1593): Updated countries (by @mmigdiso)
- **2026-07-11** - PR [#1594](https://github.com/dr5hn/countries-states-cities-database/pull/1594): Updated cities (US) (by @ebarped)

## 2026-06
- **2026-06-21** - PR [#1581](https://github.com/dr5hn/countries-states-cities-database/pull/1581): Updated cities, Updated countries (IE, US) (by @github-actions[bot])
- **2026-06-21** - PR [#1580](https://github.com/dr5hn/countries-states-cities-database/pull/1580): Updated cities (IN) (by @dr5hn)
- **2026-06-21** - PR [#1579](https://github.com/dr5hn/countries-states-cities-database/pull/1579): Updated cities (JP) (by @dr5hn)
- **2026-06-21** - PR [#1569](https://github.com/dr5hn/countries-states-cities-database/pull/1569): Updated cities (US) (by @dr5hn)
- **2026-06-21** - PR [#1573](https://github.com/dr5hn/countries-states-cities-database/pull/1573): Updated countries (by @m-lotze)
- **2026-06-21** - PR [#1574](https://github.com/dr5hn/countries-states-cities-database/pull/1574): Updated cities (IE) (by @ebarped)
- **2026-05-28** - PR [#1561](https://github.com/dr5hn/countries-states-cities-database/pull/1561): Updated cities (US) (by @dr5hn)
- **2026-05-28** - PR [#1559](https://github.com/dr5hn/countries-states-cities-database/pull/1559): Updated cities (AL, AZ, BE, BR, CN) (by @github-actions[bot])
- **2026-05-27** - PR [#1557](https://github.com/dr5hn/countries-states-cities-database/pull/1557): Updated cities (AL, AZ, BE, BR, CN) (by @ebarped)
- **2026-05-27** - PR [#1555](https://github.com/dr5hn/countries-states-cities-database/pull/1555): Updated cities (IN) (by @ebarped)

## 2026-05
- **2026-05-24** - PR [#1553](https://github.com/dr5hn/countries-states-cities-database/pull/1553): Updated cities (UY) (by @github-actions[bot])
- **2026-05-24** - PR [#1549](https://github.com/dr5hn/countries-states-cities-database/pull/1549): Updated cities (UY) (by @dr5hn)
- **2026-05-24** - PR [#1547](https://github.com/dr5hn/countries-states-cities-database/pull/1547): Updated cities, Updated countries (AU, DE, ES, ID, PS) (by @dr5hn)
- **2026-05-24** - PR [#1541](https://github.com/dr5hn/countries-states-cities-database/pull/1541): Updated cities (ES) (by @ebarped)
- **2026-05-06** - PR [#1538](https://github.com/dr5hn/countries-states-cities-database/pull/1538): Updated cities (AU) (by @dr5hn)
- **2026-05-06** - PR [#1533](https://github.com/dr5hn/countries-states-cities-database/pull/1533): Updated countries (by @dr5hn)
- **2026-05-06** - PR [#1535](https://github.com/dr5hn/countries-states-cities-database/pull/1535): Updated cities (ID, PS, UZ, VN) (by @dr5hn)
- **2026-05-06** - PR [#1537](https://github.com/dr5hn/countries-states-cities-database/pull/1537): Updated countries (by @dr5hn)
- **2026-05-05** - PR [#1530](https://github.com/dr5hn/countries-states-cities-database/pull/1530): Updated countries (by @dr5hn)
- **2026-05-05** - PR [#1503](https://github.com/dr5hn/countries-states-cities-database/pull/1503): Updated countries (by @dr5hn)
- **2026-05-05** - PR [#1502](https://github.com/dr5hn/countries-states-cities-database/pull/1502): Updated countries (by @dr5hn)
- **2026-05-05** - PR [#1501](https://github.com/dr5hn/countries-states-cities-database/pull/1501): Updated countries (by @dr5hn)
- **2026-05-05** - PR [#1526](https://github.com/dr5hn/countries-states-cities-database/pull/1526): Updated countries (by @dr5hn)
- **2026-05-05** - PR [#1518](https://github.com/dr5hn/countries-states-cities-database/pull/1518): Updated countries (by @dr5hn)
- **2026-05-05** - PR [#1515](https://github.com/dr5hn/countries-states-cities-database/pull/1515): Updated countries (by @dr5hn)
- **2026-05-05** - PR [#1511](https://github.com/dr5hn/countries-states-cities-database/pull/1511): Updated countries (by @dr5hn)
- **2026-05-05** - PR [#1504](https://github.com/dr5hn/countries-states-cities-database/pull/1504): Updated countries (by @dr5hn)
- **2026-05-05** - PR [#1497](https://github.com/dr5hn/countries-states-cities-database/pull/1497): Updated cities (UY) (by @mrodal)
- **2026-05-05** - PR [#1517](https://github.com/dr5hn/countries-states-cities-database/pull/1517): Updated cities (ES) (by @dr5hn)
- **2026-05-05** - PR [#1516](https://github.com/dr5hn/countries-states-cities-database/pull/1516): Updated cities (ES) (by @dr5hn)
- **2026-05-04** - PR [#1510](https://github.com/dr5hn/countries-states-cities-database/pull/1510): Updated cities (DE) (by @ebarped)
- **2026-04-27** - PR [#1469](https://github.com/dr5hn/countries-states-cities-database/pull/1469): Updated countries (by @dr5hn)
- **2026-04-27** - PR [#1479](https://github.com/dr5hn/countries-states-cities-database/pull/1479): Updated cities (IT) (by @dr5hn)
- **2026-04-27** - PR [#1477](https://github.com/dr5hn/countries-states-cities-database/pull/1477): Updated cities (IT) (by @dr5hn)
- **2026-04-27** - PR [#1395](https://github.com/dr5hn/countries-states-cities-database/pull/1395): Updated cities (IT) (by @dr5hn)
- **2026-04-27** - PR [#1463](https://github.com/dr5hn/countries-states-cities-database/pull/1463): Updated countries (by @dr5hn)

## v3.2 — 2026-04-27

Major data-correction release. Behaviour changes for FR/IT consumers — see notable callouts below.

**Highlights:**
- France mainland city remap region → department: 8,727 cities re-parented from 13 metropolitan regions to their correct INSEE department (#1352 PR-E, #1484). Allier (`03`), Manche (`50`), and 95 other departments now return their cities; querying by region code (`ARA`, `IDF`, `NOR`, …) now returns `[]`.
- France mainland: +455 missing communes added from data.gouv.fr (Cherbourg-en-Cotentin, Évry-Courcouronnes, Saint-Ouen-sur-Seine, …) automatically remapped to the correct department (#1352 PR-A, #1394).
- France overseas: 9 new state records + 31 city files for GF / BL / MF / PM / TF (#1352 PR-D, #1400).
- Italy cleanup: dropped 88 placeholder "Provincia di X" pseudo-cities (#1349, #1482) and merged two ISTAT-canonical comune dedup pairs — Sermide e Felonica (MN), Corteolona e Genzone (PV) (#1349, #1481).
- States `level` normalised across all FR + IT entities: `level=1` = region, `level=2` = department / province (#1489). Downstream consumers can now filter by `level` reliably.
- Postcodes: bulk imports for KH, VE, MG, MZ, MU, MT, BN, HU, CN, MM, LU and more, completing roughly 50 country-postcode datasets under #1039.
- Export pipeline: postcode export files (json/xml/yml/sqlite/sqlserver/csv) now gzip-compressed and routed to GitHub Releases; raw versions gitignored to keep the repo manageable (#1490).

---

## ⚠️ Notable: France city→department remap (PRs #1394, #1484 — issue #1352)

In April 2026 all 9,182 mainland French cities (8,727 existing + 455 newly added) were re-parented from the 13 ISO 3166-2:FR *region*-level entities (`ARA` Auvergne-Rhône-Alpes, `IDF` Île-de-France, `NOR` Normandie, etc.) to their correct INSEE *department*-level entity (`03` Allier, `13` Bouches-du-Rhône, `2A`/`2B` Corse, `75C` Paris, etc.).

This is the FR equivalent of the IT region→province remap shipped earlier in April. It fixes the long-standing bug where department-level queries (e.g. cities of `FR/03`) returned empty arrays despite both the country and department codes being valid.

**Behaviour change consumers must be aware of:**

- Querying cities by **region**-level `state_code` (`ARA`, `IDF`, `NOR`, `PDL`, `NAQ`, `BRE`, `OCC`, `GES`, `CVL`, `BFC`, `HDF`, `PAC`, `20R`) now returns `[]`. Region-level rows still exist in `states.json` but they no longer have any cities directly attached.
- To get all cities of a region, traverse the hierarchy: pull `states.json` rows where `parent_id == <region_id>` (departments of that region), then pull cities whose `state_id` is in that set.

**Companion changes:**
- `#1393` (PR-B) restored corrupted `native` field values on FR states (machine-translation artefacts like `Ain` → `Se faire`, `Aude` → `entendus`).
- `#1400` (PR-D) added the 5 missing FR-overseas city files (GF, BL, MF, PM, TF) plus their parent state records — modelled under each territory's own ISO 3166-1 country code, mirroring the existing MQ/GP/RE/YT/NC convention.
- `#1392` (PR-C) added `MULTI_LEVEL_TERRITORIES.md` documenting the dual-representation of overseas territories.
- `#1489` normalised the `level` field across FR + IT states so consumers can filter `level=1` (region) vs `level=2` (department/province).

---

## ⚠️ Notable: Italy city→province remap (PRs #1395, #1397, #1399 — issue #1349)

In April 2026 all 9,947 Italian cities were re-parented from the 20 Italian *region*-level entities (Tuscany, Lombardy, Sicily, etc.) to their correct ISO 3166-2:IT *province*-level entity (Roma → `RM`, Milan → `MI`, Agrigento → `AG`, Bolzano → `BZ`, etc.).

This is the correct administrative model — Italian cities formally belong to provinces / metropolitan cities / autonomous provinces, not to the higher-level regions — and it fixes the long-standing bug where province-level queries (e.g. cities of `IT/AG`) returned empty arrays.

**Behavior change consumers must be aware of:**

- Querying cities by **region**-level `state_code` (`82` Sicily, `25` Lombardy, `52` Tuscany, etc.) now returns `[]`. Region-level rows still exist in `states.json`, but they no longer have any cities directly attached.
- To get all cities of a region, traverse the hierarchy: pull `states.json` rows where `parent_id == <region_id>` (provinces / metropolitan cities of that region), then pull cities whose `state_id` is in that set. The `parent_id` and `level` fields on `states.json` were already correct prior to this change — no schema work required.

**Companion cleanups:**
- `#1397` restored 1,378 corrupted `native` fields on Italian cities (machine-translation artefacts like `Pero` → `Ma`).
- `#1399` dropped 6 duplicate pairs flagged by the remap (Pozzaglio + Pozzaglio ed Uniti, Torino + Turin, Naples + Napoli, etc.); 9,947 → 9,941 IT cities.

Two additional manual consolidations remain open for maintainer signoff: **Sermide e Felonica** (MN) and **Corteolona e Genzone** (PV). _(Resolved 2026-04-27 in #1481.)_

---

## 2026-04
- **2026-04-27** - PR [#1490](https://github.com/dr5hn/countries-states-cities-database/pull/1490): fix(export): gzip postcode files + gitignore raw versions (by @dr5hn)
- **2026-04-27** - PR [#1489](https://github.com/dr5hn/countries-states-cities-database/pull/1489): fix(FR/IT): normalise state.level field for region/department hierarchy (by @dr5hn)
- **2026-04-27** - PR [#1487](https://github.com/dr5hn/countries-states-cities-database/pull/1487): feat(postcodes/BN): import 547 Brunei Postal Services codes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1486](https://github.com/dr5hn/countries-states-cities-database/pull/1486): feat(postcodes/HU): import 3,569 Magyar Posta codes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1485](https://github.com/dr5hn/countries-states-cities-database/pull/1485): feat(postcodes/CN): import 22,656 China Post codes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1484](https://github.com/dr5hn/countries-states-cities-database/pull/1484): feat(FR): remap mainland cities region→department (#1352 PR-E) (by @dr5hn)
- **2026-04-27** - PR [#1483](https://github.com/dr5hn/countries-states-cities-database/pull/1483): feat(postcodes/MM): import 17,331 Myanmar Post codes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1482](https://github.com/dr5hn/countries-states-cities-database/pull/1482): fix(IT): drop 88 placeholder Provincia rows (#1349 follow-up) (by @dr5hn)
- **2026-04-27** - PR [#1481](https://github.com/dr5hn/countries-states-cities-database/pull/1481): fix(IT): merge 2 dedup pairs flagged by #1395 remap (#1349 follow-up) (by @dr5hn)
- **2026-04-27** - PR [#1480](https://github.com/dr5hn/countries-states-cities-database/pull/1480): feat(postcodes/KH): bulk-import 1,640 Cambodia postcodes via Cambodia Post (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1478](https://github.com/dr5hn/countries-states-cities-database/pull/1478): feat(postcodes/VE): bulk-import 1,187 Venezuela postcodes via IPOSTEL (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1476](https://github.com/dr5hn/countries-states-cities-database/pull/1476): feat(postcodes/MG): bulk-import 111 Madagascar postcodes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1474](https://github.com/dr5hn/countries-states-cities-database/pull/1474): feat(postcodes/MZ): bulk-import 161 Mozambique postcodes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1473](https://github.com/dr5hn/countries-states-cities-database/pull/1473): feat(postcodes/MU): bulk-import 1,874 Mauritius postcodes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1472](https://github.com/dr5hn/countries-states-cities-database/pull/1472): feat(postcodes/MT): bulk-import 26,593 Malta postcodes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1400](https://github.com/dr5hn/countries-states-cities-database/pull/1400): feat(FR-overseas): populate missing city files for GF, BL, MF, PM, TF (#1352 PR-D) (by @dr5hn)
- **2026-04-27** - PR [#1394](https://github.com/dr5hn/countries-states-cities-database/pull/1394): feat(FR): diff cities against data.gouv.fr, add missing metropolitan communes (#1352 PR-A) (by @dr5hn)
- **2026-04-27** - PR [#1393](https://github.com/dr5hn/countries-states-cities-database/pull/1393): feat(FR): polish department + region metadata vs data.gouv.fr (#1352 PR-B) (by @dr5hn)
- **2026-04-27** - PR [#1392](https://github.com/dr5hn/countries-states-cities-database/pull/1392): docs: multi-level territories policy (FR overseas, dual representation) (#1352 PR-C) (by @dr5hn)
- **2026-04-25** - PR [#1414](https://github.com/dr5hn/countries-states-cities-database/pull/1414): Updated countries (by @dr5hn)
- **2026-04-25** - PR [#1404](https://github.com/dr5hn/countries-states-cities-database/pull/1404): Updated cities, Updated states, Updated countries (CA, PY) (by @github-actions[bot])
- **2026-04-25** - PR [#1391](https://github.com/dr5hn/countries-states-cities-database/pull/1391): Updated countries (by @dr5hn)
- **2026-04-25** - PR [#1390](https://github.com/dr5hn/countries-states-cities-database/pull/1390): Updated states (by @dr5hn)
- **2026-04-25** - PR [#1389](https://github.com/dr5hn/countries-states-cities-database/pull/1389): Updated states (by @Yi-pixel)
- **2026-04-25** - PR [#1388](https://github.com/dr5hn/countries-states-cities-database/pull/1388): Updated cities (CA) (by @dr5hn)
- **2026-04-25** - PR [#1387](https://github.com/dr5hn/countries-states-cities-database/pull/1387): Updated states (by @dr5hn)
- **2026-04-25** - PR [#1386](https://github.com/dr5hn/countries-states-cities-database/pull/1386): Updated states (by @dr5hn)
- **2026-04-25** - PR [#1382](https://github.com/dr5hn/countries-states-cities-database/pull/1382): Updated cities, Updated states (CN) (by @Yi-pixel)
- **2026-04-25** - PR [#1380](https://github.com/dr5hn/countries-states-cities-database/pull/1380): Updated cities (PY) (by @juliomuhlbauer)
- **2026-04-25** - PR [#1381](https://github.com/dr5hn/countries-states-cities-database/pull/1381): Updated cities (PY) (by @juliomuhlbauer)
- **2026-04-25** - PR [#1383](https://github.com/dr5hn/countries-states-cities-database/pull/1383): Updated states (by @mrodal)

## 2026-03
- **2026-03-28** - PR [#1372](https://github.com/dr5hn/countries-states-cities-database/pull/1372): Updated cities (EG, MY, NG, PH, SA) (by @github-actions[bot])
- **2026-03-28** - PR [#1371](https://github.com/dr5hn/countries-states-cities-database/pull/1371): Updated cities (MY) (by @dr5hn)
- **2026-03-28** - PR [#1370](https://github.com/dr5hn/countries-states-cities-database/pull/1370): Updated cities (EG) (by @dr5hn)
- **2026-03-28** - PR [#1369](https://github.com/dr5hn/countries-states-cities-database/pull/1369): Updated cities (NG) (by @dr5hn)
- **2026-03-28** - PR [#1368](https://github.com/dr5hn/countries-states-cities-database/pull/1368): Updated cities (SA) (by @dr5hn)
- **2026-03-28** - PR [#1367](https://github.com/dr5hn/countries-states-cities-database/pull/1367): Updated cities (PH) (by @dr5hn)
- **2026-03-28** - PR [#1366](https://github.com/dr5hn/countries-states-cities-database/pull/1366): Updated cities (SA) (by @dr5hn)
- **2026-03-28** - PR [#1319](https://github.com/dr5hn/countries-states-cities-database/pull/1319): Updated cities (IT) (by @LodiAleardo)
- **2026-03-28** - PR [#1365](https://github.com/dr5hn/countries-states-cities-database/pull/1365): Updated cities (SA, US) (by @github-actions[bot])
- **2026-03-27** - PR [#1359](https://github.com/dr5hn/countries-states-cities-database/pull/1359): Updated cities (IN) (by @Copilot)
- **2026-03-26** - PR [#1343](https://github.com/dr5hn/countries-states-cities-database/pull/1343): Updated cities (SA) (by @JyothsnaMS)
- **2026-03-26** - PR [#1333](https://github.com/dr5hn/countries-states-cities-database/pull/1333): Updated states, Updated countries (by @Copilot)
- **2026-03-26** - PR [#1347](https://github.com/dr5hn/countries-states-cities-database/pull/1347): Updated cities (US) (by @krismach)
- **2026-03-26** - PR [#1341](https://github.com/dr5hn/countries-states-cities-database/pull/1341): Updated cities (SA) (by @milank96)
- **2026-03-26** - PR [#1356](https://github.com/dr5hn/countries-states-cities-database/pull/1356): Updated countries (by @anilkunwar421)

All notable data changes to the Countries States Cities Database will be documented in this file.
This changelog is automatically updated when PRs are merged.

