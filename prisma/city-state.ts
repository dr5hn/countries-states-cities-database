/** A source city's state fields, as in json/cities.json. */
export interface SourceCity {
  id?: number;
  name?: string;
  state_id?: number | null;
  state_code?: string | null;
  state_name?: string | null;
  country_code: string;
}

/**
 * Seeded state ids for source state ids, matched by country and state code (two states of one country may share a
 * name, never a code). Throws on a seeded key used twice or a source state that has no seeded match.
 */
export function localStateIds(
  sourceStates: { id: number; country_code: string; iso2?: string | null }[],
  seeded: { id: number; countryId: number; iso2?: string | null }[],
  countryIdByIso2: Map<string, number>,
): Map<number, number> {
  const byKey = new Map<string, number>();
  for (const s of seeded) {
    const key = `${s.countryId}:${s.iso2 ?? ''}`;
    if (!s.iso2 || byKey.has(key)) throw new Error(`seeded state ${s.id}: code ${JSON.stringify(s.iso2)} is missing or used twice in country ${s.countryId}`);
    byKey.set(key, s.id);
  }
  const out = new Map<number, number>();
  for (const s of sourceStates) {
    const local = byKey.get(`${countryIdByIso2.get(s.country_code)}:${s.iso2 ?? ''}`);
    if (local == null) throw new Error(`source state ${s.id} (${s.country_code}-${s.iso2}) has no seeded state`);
    out.set(s.id, local);
  }
  return out;
}

/** What the mapping needs: source states by id, countries that have states, and seeded ids for source state ids. */
export interface StateContext {
  sourceStates: Map<number, { country_code: string; iso2?: string | null }>;
  countriesWithStates: Set<string>;
  seededStateId: Map<number, number | undefined>;
}

/**
 * The seeded state id for a source city: null only for a city of a country with no states (v5); any missing key,
 * half-null pair, unknown state, other-country state, wrong code or unseeded state throws, so no city is dropped silently.
 */
export function cityStateId(city: SourceCity, ctx: StateContext): number | null {
  const label = `city ${city.id ?? '(new)'} ${city.name ?? ''}`.trim();
  if (!('state_id' in city) || !('state_code' in city)) throw new Error(`${label}: state_id and state_code are required`);
  const { state_id: sid, state_code: code, state_name: stateName } = city;
  if (sid == null && code == null) {
    if (!('state_name' in city) || stateName !== null) throw new Error(`${label}: a city with no state needs state_name: null`);
    if (ctx.countriesWithStates.has(city.country_code)) throw new Error(`${label}: no state, but ${city.country_code} has states`);
    return null;
  }
  if (sid == null || code == null) throw new Error(`${label}: state_id and state_code must both be set or both be null`);
  return seededState(label, sid, code, city.country_code, ctx);
}

/** The seeded id of a state given by a source (state_id, state_code) pair of a record in this country; throws otherwise. */
function seededState(label: string, sid: unknown, code: unknown, countryCode: string, ctx: StateContext): number {
  if (typeof sid !== 'number' || !Number.isInteger(sid) || sid <= 0) throw new Error(`${label}: state_id ${JSON.stringify(sid)} is not a positive integer`);
  const state = ctx.sourceStates.get(sid);
  if (!state) throw new Error(`${label}: state_id ${sid} does not exist`);
  if (state.country_code !== countryCode) throw new Error(`${label}: state ${sid} is in ${state.country_code}, not ${countryCode}`);
  if (!state.iso2) throw new Error(`${label}: state ${sid} has no state code to check against`);
  if (state.iso2 !== code) throw new Error(`${label}: state_code ${code} does not match state ${sid} (${state.iso2})`);
  const seeded = ctx.seededStateId.get(sid);
  if (seeded == null) throw new Error(`${label}: state ${sid} was not seeded`);
  return seeded;
}

/** A source county's state fields, as in json/counties.json (v5: states lists the regions of a county of several). */
export interface SourceCounty {
  id?: number;
  name?: string;
  state_id?: number | null;
  state_code?: string | null;
  states?: readonly { state_id: number; state_code: string }[] | null;
  country_code: string;
}

/**
 * The seeded state of a source county, or (v5, decision B6) the seeded regions of a county of several regions: a
 * county has its own state and no list, or a null pair and two or more distinct regions of its country. Anything else
 * throws, so no county is seeded in the wrong place.
 */
export function countyStates(county: SourceCounty, ctx: StateContext): { stateId: number | null; regions: number[] } {
  const label = `county ${county.id ?? '(new)'} ${county.name ?? ''}`.trim();
  if (!('state_id' in county) || !('state_code' in county)) throw new Error(`${label}: state_id and state_code are required`);
  const { state_id: sid, state_code: code, states } = county;
  if (sid !== null && code !== null) {
    if (states != null) throw new Error(`${label}: a county with a state cannot also list states`);
    return { stateId: seededState(label, sid, code, county.country_code, ctx), regions: [] };
  }
  if (sid !== null || code !== null) throw new Error(`${label}: state_id and state_code must both be set or both be null`);
  // only two explicit nulls reach here: a county of several regions, whose regions are rows keyed by its id
  if (typeof county.id !== 'number' || !Number.isInteger(county.id) || county.id <= 0) {
    throw new Error(`${label}: a county of several regions needs an explicit positive integer id`);
  }
  if (!Array.isArray(states)) throw new Error(`${label}: a county with no state lists two or more distinct regions in states`);
  for (const r of states) {
    if (r === null || typeof r !== 'object' || Array.isArray(r) || Object.keys(r).sort().join(',') !== 'state_code,state_id') {
      throw new Error(`${label}: each region in states needs only state_id and state_code`);
    }
  }
  const ids = states.map(r => r.state_id);
  if (states.length < 2 || new Set(ids).size !== ids.length) {
    throw new Error(`${label}: a county with no state lists two or more distinct regions in states`);
  }
  return { stateId: null, regions: states.map(r => seededState(`${label}: states entry`, r.state_id, r.state_code, county.country_code, ctx)) };
}

/** A source city as the seed reads it from json/cities.json. */
export interface SeedCity extends SourceCity {
  county_id?: number | null;
  type_local?: string | null;
  population_year?: number | null;
  latitude: string;
  longitude: string;
  wikiDataId?: string | null;
}

/** What the seed knows when it maps cities: seeded country ids, the state context and each seeded county's place. */
export interface SeedContext {
  countryMap: Map<string, number>;
  stateCtx: StateContext;
  counties: Map<number, { country_code: string; place: { stateId: number | null; regions: number[] } }>;
}

/**
 * The row the seed writes for one source city. Its state comes from cityStateId(); a county link must name a seeded
 * county of the same country whose own state, or one of whose regions (v5, decision B6), is the city's state. Anything
 * else throws, so the seed never writes a city outside its county.
 */
export function seedCityRow(city: SeedCity, ctx: SeedContext) {
  const label = `city ${city.id ?? '(new)'} ${city.name ?? ''}`.trim();
  const countryId = ctx.countryMap.get(city.country_code);
  if (!countryId) throw new Error(`${label}: country ${city.country_code} was not seeded`);
  const stateId = cityStateId(city, ctx.stateCtx);
  const cid = city.county_id ?? null;
  if (cid !== null) {
    if (typeof cid !== 'number' || !Number.isInteger(cid) || cid <= 0) throw new Error(`${label}: county_id ${JSON.stringify(cid)} is not a positive integer`);
    const county = ctx.counties.get(cid);
    if (!county) throw new Error(`${label}: county_id ${cid} does not exist`);
    if (county.country_code !== city.country_code) throw new Error(`${label}: county ${cid} is in ${county.country_code}, not ${city.country_code}`);
    const { stateId: own, regions } = county.place;
    if (stateId === null || (own !== stateId && !regions.includes(stateId))) {
      throw new Error(`${label}: its state is not in county ${cid}'s state or regions`);
    }
  }
  return {
    name: city.name, countyId: cid, stateCode: city.state_code ?? null, countryCode: city.country_code,
    typeLocal: city.type_local ?? null, populationYear: city.population_year ?? null, latitude: city.latitude,
    longitude: city.longitude, wikiDataId: city.wikiDataId, stateId, countryId,
  };
}
