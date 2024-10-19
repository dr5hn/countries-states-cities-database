import { PrismaClient } from '@prisma/client'
import fetch from 'node-fetch'

const prisma = new PrismaClient()

const API_BASE = 'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/'

async function fetchData(endpoint: string) {
  const response = await fetch(`${API_BASE}${endpoint}.json`)
  return response.json()
}

async function main() {
  // Seed Regions
  const regions = await fetchData('regions')
  for (const region of regions) {
    await prisma.region.create({
      data: {
        name: region.name,
        translations: region.translations,
        wikiDataId: region.wikiDataId,
      }
    })
  }

  // Seed Subregions
  const subregions = await fetchData('subregions')
  for (const subregion of subregions) {
    const region = await prisma.region.findUnique({ where: { name: subregion.region } })
    if (region) {
      await prisma.subregion.create({
        data: {
          name: subregion.name,
          translations: subregion.translations,
          wikiDataId: subregion.wikiDataId,
          regionId: region.id,
        }
      })
    }
  }

  // Seed Countries
  const countries = await fetchData('countries')
  for (const country of countries) {
    const region = await prisma.region.findUnique({ where: { name: country.region } })
    const subregion = await prisma.subregion.findUnique({ where: { name: country.subregion } })
    await prisma.country.create({
      data: {
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
        regionId: region?.id,
        subregionId: subregion?.id,
      }
    })
  }

  // Seed States
  const states = await fetchData('states')
  for (const state of states) {
    const country = await prisma.country.findUnique({ where: { iso2: state.country_code } })
    if (country) {
      await prisma.state.create({
        data: {
          name: state.name,
          countryCode: state.country_code,
          fipsCode: state.fips_code,
          iso2: state.iso2,
          type: state.type,
          latitude: state.latitude,
          longitude: state.longitude,
          wikiDataId: state.wikiDataId,
          countryId: country.id,
        }
      })
    }
  }

  // Seed Cities
  const cities = await fetchData('cities')
  for (const city of cities) {
    const state = await prisma.state.findFirst({
      where: {
        name: city.state_name,
        country: { iso2: city.country_code }
      }
    })
    const country = await prisma.country.findUnique({ where: { iso2: city.country_code } })
    if (state && country) {
      await prisma.city.create({
        data: {
          name: city.name,
          stateCode: city.state_code,
          countryCode: city.country_code,
          latitude: city.latitude,
          longitude: city.longitude,
          wikiDataId: city.wikiDataId,
          stateId: state.id,
          countryId: country.id,
        }
      })
    }
  }
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
