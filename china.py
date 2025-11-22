import requests
import pandas as pd
from bs4 import BeautifulSoup
import mysql.connector
import time
from io import StringIO
import re
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
# 2️⃣ Province ISO2 mapping
# --------------------------
province_iso_map = {
    # "Beijing": "BJ",
    # "Chongqing": "CQ",
    # "Shanghai": "SH",
    # "Tianjin": "TJ",


    # "Anhui": "AH",
    # "Fujian": "FJ",
    # "Gansu": "GS",
    # "Guangdong": "GD",
    # "Guizhou": "GZ",
    # "Hainan": "HI",
    # "Hebei": "HE",
    "Heilongjiang": "HL",
    # "Henan": "HA",
    # "Hubei": "HB",
    # "Hunan": "HN",
    # "Jiangsu": "JS",
    # "Jiangxi": "JX",
    # "Jilin": "JL",
    # "Liaoning": "LN",
    # "Qinghai": "QH",
    # "Shaanxi": "SN",
    # "Shandong": "SD",
    # "Shanxi": "SX",
    # "Sichuan": "SC",
    # "Yunnan": "YN",
    # "Zhejiang": "ZJ",

    "Guangxi": "GX",
    "Inner Mongolia": "NM",
    "Tibet": "XZ",
    "Ningxia": "NX",
    "Xinjiang": "XJ",
}

# --------------------------
# 3️⃣ Helper functions
# --------------------------

def get_state_id_by_iso2(iso2_code):
    cursor.execute("SELECT id FROM states WHERE iso2 = %s AND country_code = 'CN'", (iso2_code,))
    result = cursor.fetchone()
    return result["id"] if result else None

def city_exists(name, state_id, city_type=None):
    if city_type:
        cursor.execute("SELECT id FROM cities WHERE name = %s AND state_id = %s AND type = %s", (name, state_id, city_type))
    else:
        cursor.execute("SELECT id FROM cities WHERE name = %s AND state_id = %s", (name, state_id))
    return cursor.fetchone()
    

def get_province_by_iso2(iso2_code):
    cursor.execute("SELECT name FROM states WHERE iso2 = %s AND country_code = 'CN'", (iso2_code,))
    result = cursor.fetchone()
    return result["name"] if result else None


# --------------------------
# 🧭 4️⃣ Geocoding (Nominatim)
# --------------------------
geo_cache = {}

def get_lat_lon(place_name, province_name=None):
    """
    Get latitude and longitude for a given place using OpenStreetMap's Nominatim API.
    Uses in-memory cache to avoid duplicate API calls.
    """
    key = f"{place_name}_{province_name}"
    if key in geo_cache:
        return geo_cache[key]

    base_url = "https://nominatim.openstreetmap.org/search"
    query = place_name
    if province_name:
        query += f", {province_name}, China"

    url = f"{base_url}?q={quote(query)}&format=json&limit=1"

    try:
        headers = {"User-Agent": "GeoScraper/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        if data and len(data) > 0:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            geo_cache[key] = (lat, lon)
            return lat, lon
        else:
            print(f"⚠️ No coordinates found for {query}")
            geo_cache[key] = (0.0, 0.0)
            return 0.0, 0.0
    except Exception as e:
        print(f"❌ Error fetching lat/lon for {query}: {e}")
        geo_cache[key] = (0.0, 0.0)
        return 0.0, 0.0


# --------------------------
# 🧠 5️⃣ Wikidata Integration
# --------------------------
wikidata_cache = {}

def get_wikidata_id(place_name):
    """
    Get the Wikidata QID for a given Wikipedia page title.
    """
    if not place_name:
        return None
    if place_name in wikidata_cache:
        return wikidata_cache[place_name]

    base_url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "sites": "enwiki",
        "titles": place_name,
        "format": "json",
        "origin": "*"
    }

    headers = {
        "User-Agent": "MyWikidataClient/1.0 (https://example.com; contact@example.com)"
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code} error for {place_name}: {response.text[:200]}")
            return None

        data = response.json()
        entities = data.get("entities", {})
        if entities:
            qid = next(iter(entities.keys()))
            if qid.startswith("Q"):
                wikidata_cache[place_name] = qid
                return qid
        return None
    except Exception as e:
        print(f"❌ Error fetching Wikidata ID for {place_name}: {e}")
        return None


def insert_city(name, state_id, state_code, level, parent_id=None, city_type="Unknown"):
    # Avoid duplicates
    existing = city_exists(name, state_id, city_type)
    wikiDataId = get_wikidata_id(name)

    if existing:
        # Update type, level, and parent_id
        cursor.execute("""
            UPDATE cities
            SET type=%s, level=%s, parent_id=%s, wikiDataId=%s
            WHERE id=%s
        """, (city_type, level, parent_id, wikiDataId, existing["id"]))
        db.commit()
        print(f"🔄 Updated city: {name} (Level {level}, Type {city_type}) [Wikidata: {wikiDataId}]")
    else:
        province_name = get_province_by_iso2(state_code)
        lat, lon = get_lat_lon(name, province_name)
        cursor.execute("""
            INSERT INTO cities
            (name, state_id, state_code, country_id, country_code, type, level, parent_id, latitude, longitude, timezone, wikiDataId)
            VALUES
            (%s, %s, %s, 45, 'CN', %s, %s, %s, %s, %s, %s, %s)
        """, (name, state_id, state_code, city_type, level, parent_id, lat, lon, "Asia/Shanghai", wikiDataId))
        db.commit()
        print(f"✅ Inserted county-level: {name} (Level {level}, Type {city_type}), ({lat}, {lon}) [Wikidata: {wikiDataId}]")

def insert_prefecture(name, state_id, state_code, level, parent_id=None):
    # Avoid duplicates
    existing = city_exists(name, state_id)
    province_name = get_province_by_iso2(state_code)
    lat, lon = get_lat_lon(name, province_name)
    wikiDataId = get_wikidata_id(name)

    if existing:
        # Update type and level
        cursor.execute("""
            UPDATE cities
            SET type=%s, level=%s, latitude=%s, longitude=%s, wikiDataId=%s
            WHERE id=%s
        """, ("prefecture", level, lat, lon, wikiDataId, existing["id"]))
        db.commit()
        print(f"🔄 Updated prefecture: {name} (Level {level}) ({lat}, {lon}) [Wikidata: {wikiDataId}]")
    
    else:
        cursor.execute("""
            INSERT INTO cities
            (name, state_id, state_code, country_id, country_code, type, level, parent_id, latitude, longitude, timezone, wikiDataId)
            VALUES
            (%s, %s, %s, 45, 'CN', %s, %s, %s, %s, %s, %s, %s)
        """, (name, state_id, state_code, "prefecture", level, parent_id, lat, lon, "Asia/Shanghai", wikiDataId))
        db.commit()
        print(f"✅ Inserted prefecture: {name} (Level {level}) ({lat}, {lon}) [Wikidata: {wikiDataId}]")


# --------------------------
# 4️⃣ Scrape prefecture-level divisions
# --------------------------


def clean_prefecture_name(name):
    # Remove anything in parentheses
    name = re.sub(r"\(.*?\)", "", name)
    # Remove Chinese characters
    name = re.sub(r"[\u4e00-\u9fff]", "", name)
    # Remove the word "city" or "City"
    name = re.sub(r"\bcity\b", "", name, flags=re.IGNORECASE)
    # Take only the first word (usually the main name)
    name = name.strip().split()[0]
    return name

def get_prefecture_divisions(iso2_code):
    province_name = get_province_by_iso2(iso2_code)
    if not province_name:
        print(f"⚠️ Province not found for ISO2 code {iso2_code}")
        return []
    url = f"https://en.wikipedia.org/wiki/List_of_administrative_divisions_of_{province_name}"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table", {"class": "wikitable"})
    prefectures = []

    seen = set()

    for table in tables:
        df = pd.read_html(StringIO(str(table)))[0]  # Use StringIO

        prefecture_col = next((col for col in df.columns if "Prefecture" in str(col)), None)
        if not prefecture_col:
            continue


        for _, row in df.iterrows():
            pref_name = row.get(prefecture_col)
            if pd.notna(pref_name):
                cleaned_name = clean_prefecture_name(str(pref_name))
                if cleaned_name and cleaned_name not in seen:  # Only add non-empty names
                    prefectures.append({
                        "province": province_name,
                        "prefecture": cleaned_name,
                        "level": 1
                    })
                    seen.add(cleaned_name)

    return prefectures


# --------------------------
# 5️⃣ Scrape county-level divisions for each prefecture
# --------------------------

def clean_wikipedia_text(text):
    """
    Remove footnote markers like [a], [1], [note 2], etc.
    """
    return re.sub(r"\[.*?\]", "", str(text)).strip()

def get_county_divisions(iso2_code, prefecture_name):
    """
    Scrape county-level divisions belonging to a specific prefecture.
    """
    province_name = get_province_by_iso2(iso2_code)
    if not province_name:
        print(f"⚠️ Province not found for ISO2 code {iso2_code}")
        return []

    url = f"https://en.wikipedia.org/wiki/List_of_administrative_divisions_of_{province_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table", {"class": "wikitable"})
    counties = []

    def split_county_type(county_name):
        """
        Split the county name and its type based on common suffixes.
        """
        suffixes = ["County", "District", "city", "Banner", "Autonomous County", "Area", "City", "Administrative Zone"]
        for suf in suffixes:
            if county_name.endswith(suf):
                return county_name.replace(suf, "").strip(), suf.lower()
        return county_name, "Unknown"

    for table in tables:
        df = pd.read_html(StringIO(str(table)))[0]

        # Try to find columns containing "Prefecture" and "County"
        prefecture_col = next((col for col in df.columns if "Prefecture" in str(col)), None)
        county_col = next((col for col in df.columns if "County" in str(col)), None)

        if not prefecture_col or not county_col:
            continue

        for _, row in df.iterrows():
            pref = clean_wikipedia_text(row.get(prefecture_col))
            county = clean_wikipedia_text(row.get(county_col))

            if pd.notna(pref) and pd.notna(county):
                cleaned_pref = clean_prefecture_name(pref)
                cleaned_county, county_type = split_county_type(county)

                county_type = county_type.lower()

                # Only add counties belonging to the specified prefecture
                if cleaned_pref.lower() == prefecture_name.lower():
                    counties.append({
                        "province": province_name,
                        "prefecture": cleaned_pref,
                        "county": cleaned_county,
                        "type": county_type,
                        "level": 2
                    })

    return counties

# --------------------------
# 6️⃣ Main
# --------------------------

if __name__ == "__main__":
    # Limit to first 5 provinces
    for province_name, iso2_code in list(province_iso_map.items()):
        print(f"📍 Scraping province {province_name} ({iso2_code})...")
        prefectures = get_prefecture_divisions(iso2_code)
        print(f"Found {len(prefectures)} prefectures in {province_name}")

        for p in prefectures:
            state_code = iso2_code
            state_id = get_state_id_by_iso2(state_code)
            if not state_id:
                print(f"⚠️ No state found for code {state_code}")
                continue

            # Insert prefecture-level
            insert_prefecture(p["prefecture"], state_id, state_code, level=1)
            parent = city_exists(p["prefecture"], state_id, "prefecture")
            parent_id = parent["id"] if parent else None

            # Insert county-level
            counties = get_county_divisions(iso2_code, p["prefecture"])
            print(f"   ↳ {len(counties)} counties found for {p['prefecture']}")
            for c in counties:
                insert_city(c["county"], state_id, state_code, level=2, parent_id=parent_id, city_type=c["type"])
                time.sleep(0.5)

    print("✅ Done scraping all provinces with coordinates!")