#!/usr/bin/env python3
"""
Convert JSON geographical data to GeoJSON format.

This script converts JSON files containing geographical data with coordinates
to GeoJSON FeatureCollection format. It handles cities, states, and countries,
filtering out records with missing or invalid coordinate data.
"""

import json
from pathlib import Path

def json_points_to_geojson(json_path: str, geojson_path: str) -> None:
    """
    Convert JSON data with coordinates to GeoJSON FeatureCollection format.

    Args:
        json_path: Path to input JSON file containing records with latitude/longitude
        geojson_path: Path to output GeoJSON file

    Raises:
        FileNotFoundError: If input JSON file does not exist
        ValueError: If JSON data is malformed
    """
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

    skipped_count = 0

    for item in data:
        # Skip records with missing or invalid coordinates
        lat = item.get("latitude")
        lon = item.get("longitude")

        if lat is None or lon is None:
            skipped_count += 1
            continue

        try:
            lat_float = float(lat)
            lon_float = float(lon)
        except (ValueError, TypeError):
            skipped_count += 1
            continue

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon_float, lat_float]
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

    print(f"GeoJSON saved to: {geojson_path}")
    print(f"Total features: {len(geojson['features'])}")
    if skipped_count > 0:
        print(f"Skipped {skipped_count} records with missing/invalid coordinates")


if __name__ == "__main__":
    json_dir = Path("../json")
    geojson_dir = Path("../geojson")

    # Base names of the files (without extension)
    files = ["cities", "states", "countries"]

    for name in files:
        json_path = json_dir / f"{name}.json"
        geojson_path = geojson_dir / f"{name}.geojson"
        json_points_to_geojson(json_path, geojson_path)
