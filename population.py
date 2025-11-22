import mysql.connector
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
import time
import os

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
# 2️⃣ Helper functions
# --------------------------
def get_states_batch(limit=2000, offset=0):
    """Fetch a batch of states with iso2_code and country_code, using limit and offset."""
    cursor.execute("SELECT iso2, country_code FROM states LIMIT %s OFFSET %s", (limit, offset))
    return cursor.fetchall()

def get_state_name_by_iso2(iso2_code, country_code):
    """Get state/province name from iso2_code and country_code."""
    cursor.execute(
        "SELECT name FROM states WHERE iso2 = %s AND country_code = %s", 
        (iso2_code, country_code)
    )
    result = cursor.fetchone()
    return result["name"] if result else None

def get_population(iso2_code, country_code):
    """Scrape population from Wikipedia for a given state."""
    province_name = get_state_name_by_iso2(iso2_code, country_code)
    if not province_name:
        print(f"⚠️ Province not found for {iso2_code}-{country_code}")
        return None

    url = f"https://en.wikipedia.org/wiki/{quote(province_name)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch {province_name}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    infobox = soup.find("table", {"class": "infobox"})
    if not infobox:
        print(f"⚠️ No infobox found on {province_name}")
        return None

    # Find the row with "Population"
    population_row = None
    for row in infobox.find_all("tr"):
        th = row.find("th")
        if th and "Population" in th.get_text():
            population_row = row
            break

    if not population_row:
        print(f"⚠️ Population header not found in {province_name}")
        return None

    # Usually, population is in the next <tr> or same <tr> <td>
    next_row = population_row.find_next_sibling("tr")
    if not next_row or "Total" not in next_row.get_text():
        print(f"⚠️ Next row does not contain 'Total' for {province_name}")
        return None

    td = next_row.find("td")
    if td:
        text = td.get_text(separator=" ", strip=True)

        million_match = re.search(r"([\d,.]+)\s*million", text, re.IGNORECASE)
        if million_match:
            number = float(million_match.group(1).replace(",", ""))
            return int(number * 1_000_000)

        match = re.search(r"[\d,]+", text)
        if match:
            return int(match.group(0).replace(",", ""))

    print(f"⚠️ Population not found in infobox for {province_name}")
    return None


def update_population_for_state(iso2_code, country_code):
    """Fetch population and update the database."""
    population = get_population(iso2_code, country_code)
    if population is None:
        print(f"⚠️ Could not fetch population for {iso2_code}-{country_code}")
        return False

    cursor.execute(
        "UPDATE states SET population = %s WHERE iso2 = %s AND country_code = %s",
        (population, iso2_code, country_code)
    )
    db.commit()
    print(f"✅ Updated population for {iso2_code}-{country_code} to {population}")
    return True


# --------------------------
# 3️⃣ Offset tracking
# --------------------------
def get_last_processed_offset():
    """Get the last processed offset from a tracker file (or return 0 if none)."""
    try:
        with open("last_offset.txt", "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def save_last_processed_offset(offset):
    """Save the last processed offset to a file."""
    with open("last_offset.txt", "w") as f:
        f.write(str(offset))


# --------------------------
# 4️⃣ Batch updater
# --------------------------
def update_population_batch(limit=2000, delay=1):
    """Update population for a batch of states and remember progress."""
    offset = get_last_processed_offset()
    states = get_states_batch(limit, offset)
    total = len(states)

    if total == 0:
        print("🎉 All states have been processed! Resetting offset to 0.")
        save_last_processed_offset(0)
        return

    print(f"🔄 Updating population for {total} states (offset={offset}, limit={limit})...")

    for idx, state in enumerate(states, 1):
        iso2 = state['iso2']
        country = state['country_code']
        try:
            update_population_for_state(iso2, country)
        except Exception as e:
            print(f"❌ Error updating {iso2}-{country}: {e}")
        time.sleep(delay)  # prevent rate-limiting

        if idx % 10 == 0:
            print(f"📊 Progress: {idx}/{total} states updated")

    # Save new offset
    new_offset = offset + limit
    save_last_processed_offset(new_offset)
    print(f"✅ Batch complete. Next run will start from offset={new_offset}")


# --------------------------
# 5️⃣ Main execution
# --------------------------
if __name__ == "__main__":
    update_population_batch(limit=2000, delay=1)
