import json
import os
from pathlib import Path

def json_points_to_geojson(json_path: str, geojson_path: str) -> None:
    json_path = Path(json_path)
    geojson_path = Path(geojson_path)

    # --- Ensure directory exists ---
    geojson_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Load input JSON file
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. Convert to GeoJSON FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    for item in data:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(item["longitude"]),
                    float(item["latitude"])
                ]
            },
            "properties": {
                key: value
                for key, value in item.items()
                if key not in ["latitude", "longitude"]
            }
        }
        geojson["features"].append(feature)

    # 3. Save GeoJSON to file
    with geojson_path.open("w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    print("GeoJSON saved to:", geojson_path)


if __name__ == "__main__":
    json_dir = Path("./json")
    geojson_dir = Path("./geojson")

    # Base names of the files (without extension)
    files = ["cities", "states", "countries"]

    for name in files:
        json_path = json_dir / f"{name}.json"
        geojson_path = geojson_dir / f"{name}.geojson"
        json_points_to_geojson(json_path, geojson_path)
