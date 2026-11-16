import { existsSync } from "node:fs";
import { loadEnvFile } from "node:process";
import { defineConfig, env } from "prisma/config";

if (existsSync(".env")) loadEnvFile();

export default defineConfig({
  schema: "schema.prisma",
  datasource: { url: env("DATABASE_URL") },
});
