# Countries States Cities Database with Prisma

This project provides a Prisma schema and seeding script for a comprehensive database including regions, subregions, countries, states, and cities.

## Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Set up your database and update the `DATABASE_URL` in your `.env` file.

3. Generate Prisma client:
   ```
   npm run generate
   ```

4. Apply the database schema:
   ```
   npm run db:push
   ```

## Seeding the Database

To populate the database with geographical data:

```
npm run seed
```

## Notes

- The seeding process can take a while due to the large amount of data being processed.
- Ensure you have a stable internet connection as the script fetches data from GitHub.
- The database structure is designed to balance normalization and query performance.

## Customization

You can modify the `schema.prisma` file and the seeding script to fit your specific requirements. Remember to run `npm run generate` after any changes to the schema.

## Scripts

- `npm run generate`: Generate Prisma client
- `npm run db:push`: Push the schema to the database
- `npm run seed`: Run the seeding script

## Data Source

The data is sourced from the [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database) repository.

## License

[MIT](https://choosealicense.com/licenses/mit/)
