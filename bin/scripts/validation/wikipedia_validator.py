#!/usr/bin/env python3
"""
Wikipedia Data Validator

Validates geographical data (cities, states, countries) against Wikipedia API.
Used by GitHub Copilot agents for data accuracy verification.

Usage:
    python3 wikipedia_validator.py --entity "New York City" --type city --country US
    python3 wikipedia_validator.py --entity "California" --type state --country US
    python3 wikipedia_validator.py --entity "France" --type country

Requirements:
    pip install Wikipedia-API
"""

import argparse
import json
import sys
import time
from typing import Dict, Optional, List

try:
    import wikipediaapi
except ImportError:
    print("❌ Error: Wikipedia-API package not installed", file=sys.stderr)
    print("Install with: pip install Wikipedia-API", file=sys.stderr)
    sys.exit(1)


class WikipediaValidator:
    """Validates geographical data against Wikipedia API"""

    RATE_LIMIT_DELAY = 0.5  # seconds between requests
    USER_AGENT = "countries-states-cities-database/1.0 (https://github.com/dr5hn/countries-states-cities-database)"

    def __init__(self, language: str = "en"):
        """
        Initialize validator with specific Wikipedia language edition

        Args:
            language: Wikipedia language code (en, de, fr, es, etc.)
        """
        self.language = language
        self.wiki = wikipediaapi.Wikipedia(
            user_agent=self.USER_AGENT,
            language=language,
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )

    def _get_page(self, title: str) -> Optional[wikipediaapi.WikipediaPage]:
        """
        Get a Wikipedia page by title

        Args:
            title: Page title

        Returns:
            WikipediaPage object or None if not found
        """
        page = self.wiki.page(title)
        return page if page.exists() else None

    def get_article_data(self, title: str) -> Optional[Dict]:
        """
        Get comprehensive data for a Wikipedia article

        Args:
            title: Article title

        Returns:
            Dictionary with article data (coordinates, summary, etc.)
        """
        try:
            page = self._get_page(title)
            if not page:
                return None

            result = {
                "title": page.title,
                "pageid": page.pageid,
                "url": page.fullurl,
                "summary": page.summary[:500],  # First 500 chars
                "text": page.text[:1000] if page.text else "",  # First 1000 chars
                "coordinates": None,
                "latitude": None,
                "longitude": None,
                "categories": [cat for cat in page.categories.keys()][:10],  # First 10 categories
                "links": [link for link in page.links.keys()][:20],  # First 20 links
            }

            # Extract coordinates if available
            if hasattr(page, 'coordinates') and page.coordinates:
                result["latitude"] = page.coordinates.get('lat')
                result["longitude"] = page.coordinates.get('lon')
                result["coordinates"] = page.coordinates

            return result
        except Exception as e:
            print(f"❌ Error fetching article data: {e}", file=sys.stderr)
            return None

    def validate_city(self, city_name: str, country_code: str = None) -> Dict:
        """
        Validate city data against Wikipedia

        Args:
            city_name: Name of the city
            country_code: Optional country code for context

        Returns:
            Validation report with findings
        """
        print(f"\n🔍 Validating city: {city_name}")

        # Try different article title formats
        search_titles = [
            city_name,
            f"{city_name}, {country_code}" if country_code else None,
            f"{city_name} (city)",
        ]
        search_titles = [t for t in search_titles if t]  # Remove None values

        article_data = None
        for title in search_titles:
            article_data = self.get_article_data(title)
            if article_data:
                print(f"✅ Found article: {article_data['title']}")
                break
            time.sleep(self.RATE_LIMIT_DELAY)  # Rate limiting

        if not article_data:
            return {
                "status": "not_found",
                "message": f"No Wikipedia article found for '{city_name}'",
                "tried_titles": search_titles
            }

        report = {
            "status": "found",
            "query": city_name,
            "wikipedia_title": article_data["title"],
            "wikipedia_url": article_data["url"],
            "coordinates": {
                "latitude": article_data["latitude"],
                "longitude": article_data["longitude"]
            },
            "summary": article_data["summary"][:300],
            "categories": article_data["categories"],
            "related_pages": article_data["links"][:10]
        }

        return report

    def validate_state(self, state_name: str, country_code: str = None) -> Dict:
        """
        Validate state/province data against Wikipedia

        Args:
            state_name: Name of the state/province
            country_code: Optional country code for context

        Returns:
            Validation report with findings
        """
        print(f"\n🔍 Validating state: {state_name}")

        # Try different article title formats
        search_titles = [
            state_name,
            f"{state_name}, {country_code}" if country_code else None,
            f"{state_name} (state)",
        ]
        search_titles = [t for t in search_titles if t]

        article_data = None
        for title in search_titles:
            article_data = self.get_article_data(title)
            if article_data:
                print(f"✅ Found article: {article_data['title']}")
                break
            time.sleep(self.RATE_LIMIT_DELAY)

        if not article_data:
            return {
                "status": "not_found",
                "message": f"No Wikipedia article found for '{state_name}'",
                "tried_titles": search_titles
            }

        return {
            "status": "found",
            "query": state_name,
            "wikipedia_title": article_data["title"],
            "wikipedia_url": article_data["url"],
            "coordinates": {
                "latitude": article_data["latitude"],
                "longitude": article_data["longitude"]
            },
            "summary": article_data["summary"][:300],
            "categories": article_data["categories"],
            "related_pages": article_data["links"][:10]
        }

    def validate_country(self, country_name: str) -> Dict:
        """
        Validate country data against Wikipedia

        Args:
            country_name: Name of the country

        Returns:
            Validation report with findings
        """
        print(f"\n🔍 Validating country: {country_name}")

        article_data = self.get_article_data(country_name)

        if not article_data:
            return {
                "status": "not_found",
                "message": f"No Wikipedia article found for '{country_name}'"
            }

        print(f"✅ Found article: {article_data['title']}")

        return {
            "status": "found",
            "query": country_name,
            "wikipedia_title": article_data["title"],
            "wikipedia_url": article_data["url"],
            "coordinates": {
                "latitude": article_data["latitude"],
                "longitude": article_data["longitude"]
            },
            "summary": article_data["summary"][:300],
            "categories": article_data["categories"],
            "related_pages": article_data["links"][:10]
        }


def main():
    """Main entry point for CLI usage"""
    parser = argparse.ArgumentParser(
        description="Validate geographical data against Wikipedia"
    )
    parser.add_argument(
        "--entity",
        required=True,
        help="Name of the entity to validate (city, state, or country)"
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["city", "state", "country"],
        help="Type of entity"
    )
    parser.add_argument(
        "--country",
        help="Country code for context (e.g., US, FR, DE)"
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Wikipedia language edition (default: en)"
    )
    parser.add_argument(
        "--output",
        help="Output file for JSON results (optional)"
    )

    args = parser.parse_args()

    # Create validator
    validator = WikipediaValidator(language=args.language)

    # Validate based on type
    if args.type == "city":
        report = validator.validate_city(args.entity, args.country)
    elif args.type == "state":
        report = validator.validate_state(args.entity, args.country)
    else:  # country
        report = validator.validate_country(args.entity)

    # Print report
    print("\n" + "=" * 60)
    print("VALIDATION REPORT")
    print("=" * 60)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # Save to file if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Report saved to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if report["status"] == "found" else 1)


if __name__ == "__main__":
    main()
