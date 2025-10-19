#!/usr/bin/env python3
"""
Translation Enricher

Automatically adds translations for geographical entities using Wikipedia API.
Fetches translations from Wikipedia's language links.

Usage:
    python3 translation_enricher.py --file contributions/cities/US.json --type city --limit 10
    python3 translation_enricher.py --file contributions/states/states.json --type state --country-code US

Requirements:
    pip install Wikipedia-API
"""

import argparse
import json
import sys
import time
from typing import List, Dict, Optional

try:
    import wikipediaapi
except ImportError:
    print("❌ Error: Wikipedia-API package not installed", file=sys.stderr)
    print("Install with: pip install Wikipedia-API", file=sys.stderr)
    sys.exit(1)


class TranslationEnricher:
    """Adds translations to geographical data from Wikipedia"""

    # Supported language codes (common ones for geographical data)
    SUPPORTED_LANGUAGES = [
        'ar',  # Arabic
        'bn',  # Bengali
        'de',  # German
        'es',  # Spanish
        'fr',  # French
        'hi',  # Hindi
        'id',  # Indonesian
        'it',  # Italian
        'ja',  # Japanese
        'ko',  # Korean
        'nl',  # Dutch
        'pl',  # Polish
        'pt',  # Portuguese
        'ru',  # Russian
        'tr',  # Turkish
        'uk',  # Ukrainian
        'vi',  # Vietnamese
        'zh',  # Chinese (Simplified)
    ]

    USER_AGENT = "countries-states-cities-database/1.0 (https://github.com/dr5hn/countries-states-cities-database)"
    RATE_LIMIT_DELAY = 1.0  # seconds between requests

    def __init__(self, languages: Optional[List[str]] = None):
        """
        Initialize translation enricher

        Args:
            languages: List of language codes to fetch translations for
        """
        self.languages = languages or self.SUPPORTED_LANGUAGES
        self.wiki_en = wikipediaapi.Wikipedia(
            user_agent=self.USER_AGENT,
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )
        self.stats = {
            "total": 0,
            "already_had_translations": 0,
            "translations_added": 0,
            "translations_updated": 0,
            "page_not_found": 0,
            "no_langlinks": 0
        }

    def get_translations(self, entity_name: str, country_code: Optional[str] = None) -> Dict[str, str]:
        """
        Get translations for an entity from Wikipedia

        Args:
            entity_name: Name of the entity
            country_code: Optional country code for disambiguation

        Returns:
            Dictionary of language codes to translated names
        """
        translations = {}

        # Try different title formats
        titles_to_try = [
            entity_name,
            f"{entity_name}, {country_code}" if country_code else None,
            f"{entity_name} (city)" if country_code else None,
        ]
        titles_to_try = [t for t in titles_to_try if t]

        # Try each title
        page = None
        for title in titles_to_try:
            test_page = self.wiki_en.page(title)
            if test_page.exists():
                page = test_page
                break
            time.sleep(0.1)  # Small delay between attempts

        if not page:
            return translations

        # Get language links
        try:
            langlinks = page.langlinks
            for lang_code in self.languages:
                if lang_code in langlinks:
                    translated_title = langlinks[lang_code].title
                    translations[lang_code] = translated_title

            time.sleep(self.RATE_LIMIT_DELAY)  # Rate limiting

        except Exception as e:
            print(f"⚠️  Error getting translations: {e}", file=sys.stderr)

        return translations

    def enrich_record(self, record: Dict, force_update: bool = False) -> Dict:
        """
        Add translations to a single record

        Args:
            record: Data record (city or state)
            force_update: Update even if translations already exist

        Returns:
            Updated record
        """
        self.stats["total"] += 1

        # Check if translations already exist
        existing_translations = record.get("translations", {})
        if existing_translations and not force_update:
            self.stats["already_had_translations"] += 1
            return record

        # Get entity name
        entity_name = record.get("name")
        if not entity_name:
            print(f"⚠️  Record missing name field", file=sys.stderr)
            return record

        country_code = record.get("country_code")

        print(f"🔍 Fetching translations for: {entity_name}")

        # Get translations from Wikipedia
        translations = self.get_translations(entity_name, country_code)

        if translations:
            # Merge with existing translations if any
            if existing_translations:
                existing_translations.update(translations)
                record["translations"] = existing_translations
                print(f"🔄 Updated translations for {entity_name}: {len(translations)} languages")
                self.stats["translations_updated"] += 1
            else:
                record["translations"] = translations
                print(f"✅ Added translations for {entity_name}: {len(translations)} languages")
                self.stats["translations_added"] += 1

            # Show sample translations
            sample = list(translations.items())[:3]
            for lang, trans in sample:
                print(f"   {lang}: {trans}")

        else:
            self.stats["no_langlinks"] += 1
            print(f"ℹ️  No translations found for: {entity_name}")
            # Initialize empty translations dict if it doesn't exist
            if "translations" not in record:
                record["translations"] = {}

        return record

    def enrich_file(self, file_path: str, force_update: bool = False,
                   country_code: Optional[str] = None, limit: Optional[int] = None) -> None:
        """
        Enrich all records in a JSON file

        Args:
            file_path: Path to JSON file
            force_update: Update existing translations
            country_code: Filter by country code (for states.json)
            limit: Maximum number of records to process
        """
        print(f"\n📂 Processing: {file_path}")
        print(f"🌍 Languages: {', '.join(self.languages)}")

        # Load data
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

        # Filter by country if specified
        if country_code:
            original_count = len(data)
            data = [r for r in data if r.get("country_code") == country_code]
            print(f"🔍 Filtered to {country_code}: {len(data)} of {original_count} records")

        # Apply limit if specified
        if limit:
            data = data[:limit]
            print(f"⚠️  Limited to first {limit} records for testing")

        # Enrich records
        enriched_data = []
        for i, record in enumerate(data, 1):
            print(f"\n[{i}/{len(data)}]", end=" ")
            enriched_record = self.enrich_record(record, force_update=force_update)
            enriched_data.append(enriched_record)

        # Save if changes were made
        if self.stats["translations_added"] > 0 or self.stats["translations_updated"] > 0:
            # If we filtered/limited, we need to update only those records in the original file
            if country_code or limit:
                # Re-load original data
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_data = json.load(f)

                # Update enriched records
                enriched_map = {r.get("id"): r for r in enriched_data if r.get("id")}
                for i, record in enumerate(all_data):
                    if record.get("id") in enriched_map:
                        all_data[i] = enriched_map[record["id"]]

                final_data = all_data
            else:
                final_data = enriched_data

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=2)

            print(f"\n💾 Saved changes to: {file_path}")
        else:
            print(f"\nℹ️  No changes needed")

        # Print statistics
        self.print_stats()

    def print_stats(self) -> None:
        """Print enrichment statistics"""
        print("\n" + "=" * 60)
        print("TRANSLATION ENRICHMENT STATISTICS")
        print("=" * 60)
        print(f"Total records:              {self.stats['total']}")
        print(f"Already had translations:   {self.stats['already_had_translations']}")
        print(f"Translations added:         {self.stats['translations_added']} ✅")
        print(f"Translations updated:       {self.stats['translations_updated']} 🔄")
        print(f"No translations found:      {self.stats['no_langlinks']} ℹ️")
        print("=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Add translations to geographical data from Wikipedia"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to JSON file (cities or states)"
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["city", "state", "country"],
        help="Type of data"
    )
    parser.add_argument(
        "--country-code",
        help="Filter by country code (for states.json)"
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        help="List of language codes (default: all supported)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of records to process (for testing)"
    )
    parser.add_argument(
        "--force-update",
        action="store_true",
        help="Update existing translations"
    )

    args = parser.parse_args()

    # Create enricher
    enricher = TranslationEnricher(languages=args.languages)

    # Process file
    enricher.enrich_file(
        file_path=args.file,
        force_update=args.force_update,
        country_code=args.country_code,
        limit=args.limit
    )


if __name__ == "__main__":
    main()
