import json
from pathlib import Path

def json_to_toon(json_text: str, delimiter: str = ",") -> str:
    data = json.loads(json_text)

    if not isinstance(data, list) or not data:
        raise ValueError("Expected non-empty top-level JSON array")

    # Use the key order from the first object
    columns = list(data[0].keys())

    def format_value(v):
        if isinstance(v, bool):
            s = "true" if v else "false"
        elif v is None:
            s = ""
        else:
            s = str(v)

        if not s:
            return s

        if s[0].isspace() or s[-1].isspace() or delimiter in s or "\n" in s:
            s = s.replace('"', '\\"')
            return f'"{s}"'
        return s

    def encode_row(obj):
        vals = []
        for col in columns:
            v = obj.get(col)

            if isinstance(v, dict):
                inner = "|".join(f"{k}={v[k]}" for k in v)
                vals.append(format_value(inner))
            else:
                vals.append(format_value(v))
        return delimiter.join(vals)

    lines = []
    lines.append(f"[{len(data)}]" + "{" + ",".join(columns) + "}:")
    for row in data:
        lines.append(encode_row(row))

    return "\n".join(lines)


def json_file_to_toon_file(
    json_path: str,
    toon_path: str,
    delimiter: str = ","
) -> None:
    json_path = Path(json_path)
    toon_path = Path(toon_path)

    # Ensure destination directory exists
    toon_path.parent.mkdir(parents=True, exist_ok=True)

    # Read JSON file
    with json_path.open("r", encoding="utf-8") as f:
        json_text = f.read()

    # Convert to TOON
    toon_text = json_to_toon(json_text, delimiter=delimiter)

    # Write TOON file
    with toon_path.open("w", encoding="utf-8") as f:
        f.write(toon_text)


if __name__ == "__main__":
    json_dir = Path("../json")
    toon_dir = Path("../toon")

    # List of base filenames (without extension)
    files = ["countries", "cities", "states"]

    for name in files:
        json_path = json_dir / f"{name}.json"
        toon_path = toon_dir / f"{name}.toon"

        json_file_to_toon_file(json_path, toon_path)
        print(f"Written TOON data to: {toon_path}")
