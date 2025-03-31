import { PrismaClient } from '@prisma/client';
import fetch from 'node-fetch';

const prisma = new PrismaClient();
const API_BASE = 'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/';

async function fetchData(endpoint: string) {
  const response = await fetch(`${API_BASE}${endpoint}.json`);
  return response.json();
}

async function main() {
  console.log('Seeding started...');

  // Seed Regions
  const regions = await fetchData('regions');
  await prisma.region.createMany({
    data: regions.map(({ name, translations, wikiDataId }) => ({
      name,
      translations,
      wikiDataId,
    })),
    skipDuplicates: true,
  });

  // Fetch all regions after insertion
  const regionMap = new Map((await prisma.region.findMany()).map(r => [r.name, r.id]));

  // Seed Subregions
  const subregions = await fetchData('subregions');
  const subregionData = subregions
    .map(({ name, translations, wikiDataId, region }) => {
      const regionId = regionMap.get(region);
      return regionId ? { name, translations, wikiDataId, regionId } : null;
    })
    .filter(Boolean);

  await prisma.subregion.createMany({ data: subregionData, skipDuplicates: true });

  // Fetch all subregions after insertion
  const subregionMap = new Map((await prisma.subregion.findMany()).map(sr => [sr.name, sr.id]));

  // Seed Countries
  const countries = await fetchData('countries');
  const countryData = countries.map(country => ({
    name: country.name,
    iso3: country.iso3,
    iso2: country.iso2,
    numericCode: country.numeric_code,
    phoneCode: country.phone_code,
    capital: country.capital,
    currency: country.currency,
    currencyName: country.currency_name,
    currencySymbol: country.currency_symbol,
    tld: country.tld,
    native: country.native,
    region: country.region,
    subregion: country.subregion,
    latitude: country.latitude,
    longitude: country.longitude,
    emoji: country.emoji,
    emojiU: country.emojiU,
    timezones: country.timezones,
    translations: country.translations,
    wikiDataId: country.wikiDataId,
    regionId: regionMap.get(country.region) || null,
    subregionId: subregionMap.get(country.subregion) || null,
  }));

  await prisma.country.createMany({ data: countryData, skipDuplicates: true });

  // Fetch all countries after insertion
  const countryMap = new Map((await prisma.country.findMany()).map(c => [c.iso2, c.id]));

  // Seed States
  const states = await fetchData('states');
  const stateData = states
    .map(({ name, country_code, fips_code, iso2, type, latitude, longitude, wikiDataId }) => {
      const countryId = countryMap.get(country_code);
      return countryId
        ? { name, countryCode: country_code, fipsCode: fips_code, iso2, type, latitude, longitude, wikiDataId, countryId }
        : null;
    })
    .filter(Boolean);

  await prisma.state.createMany({ data: stateData, skipDuplicates: true });

  // Fetch all states after insertion
  const stateMap = new Map((await prisma.state.findMany()).map(s => [`${s.name}-${s.countryId}`, s.id]));

  // Seed Cities
  const cities = await fetchData('cities');
  const cityData = cities
    .map(({ name, state_name, country_code, state_code, latitude, longitude, wikiDataId }) => {
      const countryId = countryMap.get(country_code);
      const stateId = stateMap.get(`${state_name}-${countryId}`);
      return stateId && countryId
        ? { name, stateCode: state_code, countryCode: country_code, latitude, longitude, wikiDataId, stateId, countryId }
        : null;
    })
    .filter(Boolean);

  await prisma.city.createMany({ data: cityData, skipDuplicates: true });

  console.log('Seeding completed!');
}

main()
  .catch((e) => {
    console.error('Seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
