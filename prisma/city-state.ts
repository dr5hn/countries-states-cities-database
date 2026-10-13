/** A source city's state fields, as in json/cities.json. */
export interface SourceCity {
  id?: number;
  name?: string;
  state_id?: number | null;
  state_code?: string | null;
  state_name?: string | null;
  country_code: string;
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
    if (stateName != null) throw new Error(`${label}: state_name is set but the state is null`);
    if (ctx.countriesWithStates.has(city.country_code)) throw new Error(`${label}: no state, but ${city.country_code} has states`);
    return null;
  }
  if (sid == null || code == null) throw new Error(`${label}: state_id and state_code must both be set or both be null`);
  if (typeof sid !== 'number' || !Number.isInteger(sid) || sid <= 0) throw new Error(`${label}: state_id ${JSON.stringify(sid)} is not a positive integer`);
  const state = ctx.sourceStates.get(sid);
  if (!state) throw new Error(`${label}: state_id ${sid} does not exist`);
  if (state.country_code !== city.country_code) throw new Error(`${label}: state ${sid} is in ${state.country_code}, not ${city.country_code}`);
  if (state.iso2 != null && state.iso2 !== code) throw new Error(`${label}: state_code ${code} does not match state ${sid} (${state.iso2})`);
  const seeded = ctx.seededStateId.get(sid);
  if (seeded == null) throw new Error(`${label}: state ${sid} was not seeded`);
  return seeded;
}
