# Country State City on Neon

Load the full Country State City dataset — 250+ countries, 5.3k states, and
153.8k cities — into a free [Neon](https://neon.com) serverless Postgres database
in about five minutes.

The dataset is small, static, and read-heavy, which makes it a great fit for
Neon's autoscaling and database branching. Use it as a ready-made geo backend for
your own apps, or as a branchable reference database for testing.

## Prerequisites

- A Neon account and a project ([neon.com](https://neon.com) — the free tier is
  enough for the full dataset).
- The `psql` client (ships with any PostgreSQL install:
  `brew install libpq` on macOS, `apt install postgresql-client` on Debian/Ubuntu).
- This repository cloned locally, or just the files under [`psql/`](./psql).

## 1. Get your Neon connection string

From the Neon console: **Project → Connect → Connection string**. It looks like:

```
postgresql://<user>:<password>@<endpoint>.neon.tech/<db>?sslmode=require
```

Export it so the commands below stay copy-pasteable:

```bash
export DATABASE_URL="postgresql://<user>:<password>@<endpoint>.neon.tech/<db>?sslmode=require"
```

## 2. Load the data (one command)

[`psql/world.sql`](./psql/world.sql) is a complete `pg_dump` — schema **and**
data — so a single command creates every table and populates it:

```bash
psql "$DATABASE_URL" -f psql/world.sql
```

Prefer a smaller download? Use the gzipped dump:

```bash
gunzip -c psql/world.sql.gz | psql "$DATABASE_URL"
```

### Load only part of the dataset

If you don't need every city, load the schema first, then just the tables you
want:

```bash
psql "$DATABASE_URL" -f psql/schema.sql       # tables + constraints, no rows
psql "$DATABASE_URL" -f psql/countries.sql    # ~250 countries
psql "$DATABASE_URL" -f psql/states.sql       # ~5.3k states
# psql "$DATABASE_URL" -f psql/cities.sql     # ~153.8k cities (largest file)
```

## 3. Verify

```bash
psql "$DATABASE_URL" -c \
  "SELECT
     (SELECT count(*) FROM countries) AS countries,
     (SELECT count(*) FROM states)    AS states,
     (SELECT count(*) FROM cities)    AS cities;"
```

Expected output:

```
 countries | states | cities
-----------+--------+--------
       250 |   5341 | 153824
```

(Counts track the latest release and may differ slightly.)

## Using it with Prisma

This repo ships a Prisma schema at [`prisma/schema.prisma`](./prisma). Point it at
Neon and generate a client:

```bash
# .env
DATABASE_URL="postgresql://<user>:<password>@<endpoint>.neon.tech/<db>?sslmode=require"
```

```bash
npx prisma db pull        # introspect the loaded tables
npx prisma generate       # generate the client
```

For serverless runtimes (Vercel, Cloudflare Workers), use Neon's driver adapter:

```bash
npm install @prisma/adapter-neon @neondatabase/serverless
```

```ts
import { PrismaClient } from "@prisma/client";
import { PrismaNeon } from "@prisma/adapter-neon";

const adapter = new PrismaNeon({ connectionString: process.env.DATABASE_URL });
const prisma = new PrismaClient({ adapter });

const indianStates = await prisma.states.findMany({
  where: { country: { iso2: "IN" } },
  select: { name: true },
});
```

## Tips

- **Branch instead of reseeding.** Use Neon's database branching to spin up an
  instant copy for tests or a new environment — no need to re-import the dump.
- **Add indexes for lookups.** For name search, a trigram index helps:
  `CREATE EXTENSION IF NOT EXISTS pg_trgm; CREATE INDEX ON cities USING gin (name gin_trgm_ops);`
- **Keep it read-only in production.** The data changes rarely, so a read replica
  or heavy caching in front of Neon serves this workload cheaply.

## License

The dataset is provided under the [Open Database License (ODbL) v1.0](./LICENSE).
Attribution to the Country State City project is required for adaptations.
