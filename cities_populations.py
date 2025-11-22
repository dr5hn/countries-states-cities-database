import os
import re
import sys
import time
import math
import requests
import mysql.connector
from urllib.parse import quote

# --------------------------
# 1️⃣ MySQL connection
# --------------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="world"
)
cursor = db.cursor(dictionary=True, buffered=True)

# --------------------------
# 2️⃣ Config / constants
# --------------------------
RAPIDAPI_KEY = "8c462e143bmsh91de42229aa02a3p198edajsn8de0160498eb"
GEODB_HOST = "wft-geo-db.p.rapidapi.com"
GEODB_BASE = f"https://{GEODB_HOST}"
GEODB_CITIES_ENDPOINT = f"{GEODB_BASE}/v1/geo/cities"

# tune these if you hit rate limits
MAX_RETRIES = 5
INITIAL_BACKOFF_SECS = 1.0
TIMEOUT_SECS = 12

if not RAPIDAPI_KEY:
    print("❌ Missing RAPIDAPI_KEY environment variable")
    sys.exit(1)

session = requests.Session()
session.headers.update({
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": GEODB_HOST,
    "User-Agent": "city-pop-updater/1.0"
})

# --------------------------
# 3️⃣ Helper functions
# --------------------------
def get_cities_batch(limit=50, offset=0):
    """Fetch a batch of cities with id, name, country_code (ISO-2 expected)."""
    cursor.execute(
        "SELECT id, name, country_code FROM cities ORDER BY id ASC LIMIT %s OFFSET %s",
        (limit, offset)
    )
    return cursor.fetchall()

# print(get_cities_batch(limit=50, offset=0))

def _request_with_backoff(url, params):
    """HTTP GET with exponential backoff for 429/5xx."""
    backoff = INITIAL_BACKOFF_SECS
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, params=params, timeout=TIMEOUT_SECS)
        except requests.RequestException as e:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(backoff)
            backoff *= 2
            continue

        if resp.status_code == 200:
            return resp.json()

        # Respect rate limiting
        if resp.status_code in (429, 503, 502, 504, 500):
            if attempt == MAX_RETRIES:
                resp.raise_for_status()
            # honor Retry-After if present
            retry_after = resp.headers.get("Retry-After")
            wait = float(retry_after) if retry_after else backoff
            time.sleep(wait)
            backoff = min(backoff * 2, 30.0)
            continue

        # Other client errors: fail fast with helpful info
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise RuntimeError(f"GeoDB error {resp.status_code}: {detail}")

def get_population_from_geodb(city_name: str, country_code: str):
    """
    Use GeoDB Cities to fetch population:
    - filter by countryIds (ISO-2)
    - try exact match (case-insensitive) among returned data
    - otherwise take the top result sorted by population desc
    Returns: int population or None
    """
    if not city_name:
        return (None, None, None)

    # First try a tighter query: exact name filter where possible
    # GeoDB supports "namePrefix". We'll request a few results and pick best match.
    params = {
        "namePrefix": city_name,
        "countryIds": country_code,   # ISO-2 like 'US', 'IN'
        "limit": 10,
        "sort": "-population",
        "hateoasMode": "false"
    }

    data = _request_with_backoff(GEODB_CITIES_ENDPOINT, params=params)
    matches = data.get("data", []) if isinstance(data, dict) else []

    if not matches:
        # Try URL-encoded whole name as a final hail mary (some locales)
        params_alt = {
            "namePrefix": quote(city_name),
            "countryIds": country_code,
            "limit": 10,
            "sort": "-population",
            "hateoasMode": "false"
        }
        data = _request_with_backoff(GEODB_CITIES_ENDPOINT, params_alt)
        matches = data.get("data", []) if isinstance(data, dict) else []

    if not matches:
        return (None, None, None)

    # Prefer exact (case-insensitive) name match
    exact = [m for m in matches if m.get("name", "").lower() == city_name.lower()]
    ordered = exact if exact else matches

    # Pick the first one that has an integer population; otherwise just take first
    candidate = None
    for m in ordered:
        if isinstance(m.get("population"), int):
            candidate = m
            break
    if candidate is None:
        candidate = ordered[0]

    population = candidate.get("population") if isinstance(candidate.get("population"), int) else None
    wiki_data_id = candidate.get("wikiDataId") if isinstance(candidate.get("wikiDataId"), str) else None
    raw_type = candidate.get("type")
    place_type = raw_type.lower() if isinstance(raw_type, str) else None

    # print(population, wiki_data_id, place_type)
    return (population, wiki_data_id, place_type)

# print(get_population_from_geodb("Canillo", "AD"))

def update_population_for_city(city_id, city_name, country_code):
    """Fetch population via GeoDB and update the DB."""
    try:
        population, wiki_data_id, place_type = get_population_from_geodb(city_name, country_code)
    except Exception as e:
        print(f"❌ GeoDB lookup failed for {city_name} ({country_code}): {e}")
        return False

    if population is None:
        print(f"⚠️ No population found for {city_name} ({country_code})")
        return False

    try:
        cursor.execute(
            "UPDATE cities SET population = %s, wikiDataId = %s, type = %s  WHERE id = %s",
            (population, wiki_data_id, place_type,  city_id)
        )
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ DB update failed for {city_name} ({country_code}): {e}")
        return False

    print(f"✅ Updated population for {city_name} ({country_code}) to {population}")
    return True

# print(update_population_for_city(3, "Canillo", "AD"))

# --------------------------
# 4️⃣ Batch updater (fixed batch size = 50)
# --------------------------
def update_population_batch(batch_number, limit=50, delay=0.5):
    """Update population for a fixed batch of cities (50 per batch)."""
    if batch_number < 1:
        print("❌ Invalid batch number. Must be >= 1")
        return

    offset = (batch_number - 1) * limit
    cities = get_cities_batch(limit, offset)
    total = len(cities)

    if total == 0:
        print(f"🎉 No cities found for batch-{batch_number} (offset={offset}).")
        return

    print(f"🔄 Processing batch-{batch_number}: {total} cities (offset={offset}, limit={limit})...")

    for idx, city in enumerate(cities, 1):
        city_id = city['id']
        city_name = city['name']
        country = city['country_code']  # make sure this is ISO-2 for GeoDB

        try:
            update_population_for_city(city_id, city_name, country)
        except Exception as e:
            print(f"❌ Error updating {city_name} ({country}): {e}")

        time.sleep(delay)  # be nice to the API

        if idx % 50 == 0 or idx == total:
            print(f"📊 Progress: {idx}/{total} cities processed")

    print(f"✅ Batch-{batch_number} complete. Processed {total} cities.")

# --------------------------
# 5️⃣ Main execution
# --------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python3 file_name.py batch-1")
        sys.exit(1)

    arg = sys.argv[1]
    match = re.match(r"batch-(\d+)", arg)
    if not match:
        print("❌ Invalid batch format. Use 'batch-1', 'batch-2', etc.")
        sys.exit(1)

    batch_number = int(match.group(1))
    update_population_batch(batch_number=batch_number, limit=50, delay=0.5)
