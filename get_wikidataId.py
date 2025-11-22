import mysql.connector
import requests

# ---------- Database Configuration ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "world"
}



# ---------- Wikidata API Helper Function ----------
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
        # if response.status_code != 200:
        #     print(f"❌ HTTP {response.status_code} error for {place_name}: {response.text[:200]}")
        #     return None

        response.raise_for_status()
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


def validate_wikidata_id(qid):
    """
    Check if a Wikidata ID (QID) exists on Wikidata.
    Returns True if valid, False otherwise.
    """
    if not qid or not qid.startswith("Q"):
        return False
    base_url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        response = requests.get(base_url, timeout=10)
        return response.status_code == 200
    except:
        return False


# ---------- Update Wikidata IDs ----------
def update_wikidata_ids():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    # 1️⃣ STATES
    cursor.execute("SELECT id, name, wikiDataId FROM states LIMIT 10")
    states = cursor.fetchall()

    for state in states:
        name = state['name']
        current_qid = state['wikiDataId']
        update_needed = False

        # If missing or invalid QID, fetch a new one
        if not current_qid or not validate_wikidata_id(current_qid):
            new_qid = get_wikidata_id(name)
            if new_qid:
                print(f"✅ Updating {name} with Wikidata ID {new_qid}")
                cursor.execute("UPDATE states SET wikiDataId = %s WHERE id = %s", (new_qid, state['id']))
                update_needed = True
            else:
                print(f"⚠️ No Wikidata ID found for {name}")
        else:
            print(f"✅ {name} already has a valid Wikidata ID ({current_qid})")

        if update_needed:
            conn.commit()

    # 2️⃣ CITIES (Optional)
    # cursor.execute("SELECT id, name, wikiDataId FROM cities")
    # cities = cursor.fetchall()
    # for city in cities:
    #     name = city['name']
    #     current_qid = city['wikiDataId']
    #     if not current_qid or not validate_wikidata_id(current_qid):
    #         new_qid = get_wikidata_id(name)
    #         if new_qid:
    #             print(f"✅ Updating {name} with Wikidata ID {new_qid}")
    #             cursor.execute("UPDATE cities SET wikiDataId = %s WHERE id = %s", (new_qid, city['id']))
    #             conn.commit()
    #         else:
    #             print(f"⚠️ No Wikidata ID found for {name}")

    conn.close()
    print("\n🎉 Wikidata ID synchronization complete!")

if __name__ == "__main__":
    update_wikidata_ids()
