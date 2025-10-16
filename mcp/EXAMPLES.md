# Wikipedia MCP Integration Examples

This document provides practical examples of using the Wikipedia MCP server with the Countries States Cities Database.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Data Validation Examples](#data-validation-examples)
- [Data Enrichment Examples](#data-enrichment-examples)
- [Research and Analysis](#research-and-analysis)
- [Documentation Generation](#documentation-generation)

## Basic Usage

### Simple Information Retrieval

Once the Wikipedia MCP server is configured with Claude Desktop, you can ask questions like:

```
Tell me about Paris, France using Wikipedia
```

Claude will retrieve information from Wikipedia about Paris and provide a summary including:
- Population
- Geography
- History
- Administrative divisions
- Notable features

### Searching for Multiple Locations

```
Get Wikipedia summaries for the top 5 most populous cities in Japan
```

Claude will:
1. Identify the cities (Tokyo, Yokohama, Osaka, Nagoya, Sapporo)
2. Retrieve Wikipedia information for each
3. Provide a comparative summary

## Data Validation Examples

### Validating City Information

**Scenario**: You want to verify that a city's information in the database matches Wikipedia.

**Prompt**:
```
I have Tokyo in my database with these details:
- Country: Japan
- State: Tokyo
- Timezone: Asia/Tokyo
- Coordinates: 35.6762°N, 139.6503°E

Can you verify these details using Wikipedia?
```

**Use Case**: Ensures data accuracy by cross-referencing with Wikipedia's curated content.

### Checking Administrative Divisions

**Prompt**:
```
According to Wikipedia, what are the administrative divisions of Germany at the state level?
Compare this with my database query results:
[paste query results from: SELECT name FROM world.states WHERE country_code='DE']
```

**Use Case**: Validates that all states/provinces are correctly represented in the database.

### Verifying Timezone Information

**Prompt**:
```
What timezone does Wikipedia list for Sydney, Australia?
```

**Use Case**: Cross-checks timezone data against Wikipedia references.

## Data Enrichment Examples

### Adding Historical Context

**Prompt**:
```
For the following 5 European capital cities, provide historical founding information from Wikipedia:
- Paris, France
- Berlin, Germany
- Rome, Italy
- Madrid, Spain
- London, United Kingdom
```

**Use Case**: Enriches database with historical context that could be added as metadata.

### Population Data Cross-Reference

**Prompt**:
```
Get the most recent population figures from Wikipedia for these cities:
1. Mumbai, India
2. São Paulo, Brazil
3. Cairo, Egypt
4. Lagos, Nigeria
5. Mexico City, Mexico

Compare these with my database values:
[paste database values]
```

**Use Case**: Identifies population data that may need updating.

### Cultural Information

**Prompt**:
```
Retrieve cultural and demographic highlights from Wikipedia for:
- Dubai, UAE
- Singapore, Singapore
- Hong Kong, China

Focus on:
- Primary languages
- Major ethnic groups
- Economic characteristics
```

**Use Case**: Adds cultural context that can inform internationalization features.

## Research and Analysis

### Regional Analysis

**Prompt**:
```
Using Wikipedia, provide an overview of the Nordic countries:
- List all countries
- Capital cities
- Form of government
- Population size
- Languages spoken

Then compare with my database entries for these countries.
```

**Use Case**: Comprehensive regional analysis for data validation and enrichment.

### Geographic Feature Analysis

**Prompt**:
```
For coastal cities in the database with population > 1 million, 
get Wikipedia information about their maritime significance:
- Miami, USA
- Barcelona, Spain
- Mumbai, India
- Sydney, Australia
- Rio de Janeiro, Brazil
```

**Use Case**: Identifies additional attributes that could enhance the database schema.

### Historical Name Changes

**Prompt**:
```
Using Wikipedia, identify historical name changes for these cities:
- Istanbul (formerly Constantinople)
- Mumbai (formerly Bombay)
- Ho Chi Minh City (formerly Saigon)
- Chennai (formerly Madras)

Provide both historical and current official names.
```

**Use Case**: Ensures the database uses current, official names while being aware of historical variants.

## Documentation Generation

### Country Profile Generation

**Prompt**:
```
Create a comprehensive country profile for Switzerland using Wikipedia, including:
- Official names in all national languages
- Geographic location and neighboring countries
- Capital and major cities
- Administrative divisions (cantons)
- Languages
- Currency
- Government type

Format this as markdown documentation.
```

**Use Case**: Generates rich documentation for the database's countries.

### City Highlights

**Prompt**:
```
For the top 10 tourist destination cities in the database, 
create brief highlight cards using Wikipedia information:
- Paris, France
- London, United Kingdom
- Tokyo, Japan
- New York, USA
- Barcelona, Spain
- Rome, Italy
- Prague, Czech Republic
- Dubai, UAE
- Amsterdam, Netherlands
- Bangkok, Thailand

Include: brief description, notable landmarks, and primary language.
```

**Use Case**: Creates user-facing content for applications using the database.

## Advanced Integration Workflows

### Batch Validation Script

```bash
#!/bin/bash
# Example: Validate multiple cities using Wikipedia MCP

# List of cities to validate
cities=(
    "Tokyo,JP"
    "Paris,FR"
    "London,GB"
    "New York,US"
    "Berlin,DE"
)

# For each city, query database and ask Claude to verify with Wikipedia
for city_data in "${cities[@]}"; do
    IFS=',' read -r city country <<< "$city_data"
    
    echo "Validating: $city, $country"
    
    # Query database
    result=$(mysql -uroot -proot -e "SELECT * FROM world.cities WHERE name='$city' AND country_code='$country';" 2>/dev/null)
    
    # Ask Claude to verify (this would be done through Claude Desktop)
    echo "Database entry for $city: $result"
    echo "Ask Claude: Verify this information using Wikipedia for $city"
    echo "---"
done
```

### Data Enrichment Pipeline

```python
#!/usr/bin/env python3
"""
Example: Enrich database with Wikipedia information
Note: This requires Claude API or similar integration
"""

import json
import mysql.connector

def get_cities_needing_enrichment():
    """Get cities without description field"""
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="world"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, name, country_code 
        FROM cities 
        WHERE description IS NULL 
        LIMIT 100
    """)
    cities = cursor.fetchall()
    conn.close()
    return cities

def main():
    cities = get_cities_needing_enrichment()
    
    print(f"Found {len(cities)} cities needing enrichment")
    print("\nCities to enrich:")
    for city in cities[:10]:  # Show first 10
        print(f"- {city['name']}, {city['country_code']}")
    
    print("\nNext steps:")
    print("1. Use Claude Desktop with Wikipedia MCP to get descriptions")
    print("2. Update the database with enriched information")
    print("3. Sync back to JSON files")

if __name__ == "__main__":
    main()
```

## Tips for Effective Usage

### Best Practices

1. **Be Specific**: Include city and country names to avoid ambiguity
   ```
   Good: "Get Wikipedia info for Paris, France"
   Avoid: "Get info for Paris" (could be Paris, Texas)
   ```

2. **Request Structured Data**: Ask for information in a specific format
   ```
   "From Wikipedia, list the states of Germany in this format:
   - Name: [State Name]
   - Capital: [Capital City]
   - Population: [Number]"
   ```

3. **Cross-Reference**: Always compare Wikipedia data with database data
   ```
   "Compare Wikipedia's list of Italian regions with my database query:
   [paste query results]
   Identify any discrepancies."
   ```

4. **Batch Queries**: Group related queries for efficiency
   ```
   "For all Scandinavian countries (Norway, Sweden, Denmark, Finland, Iceland),
   get Wikipedia information about their capital cities."
   ```

### Common Patterns

#### Pattern 1: Verification
```
Database says: [data]
Wikipedia says: [query]
Are they consistent?
```

#### Pattern 2: Enrichment
```
Get additional context from Wikipedia for: [entity]
Focus on: [specific aspects]
```

#### Pattern 3: Research
```
Using Wikipedia, research [topic] across multiple locations: [list]
Summarize findings in a table.
```

## Integration with Export Tools

### Enriched JSON Export

After enriching data with Wikipedia information, you can export enhanced datasets:

```bash
# 1. Enrich data using Claude + Wikipedia MCP
# 2. Update database
python3 bin/scripts/sync/import_json_to_mysql.py

# 3. Export enriched data
cd bin
php console export:json

# 4. Verify the enriched export
cat json/cities.json | jq '.[] | select(.name=="Paris")'
```

### Documentation Export

```bash
# Generate documentation with Wikipedia context
# This could be automated as a custom export command

# Example: Export countries with Wikipedia descriptions
cd bin
php console export:json

# Then use the JSON with Claude to create enriched docs
```

## Troubleshooting

### MCP Server Not Responding

1. Check if the server is running:
   ```bash
   ps aux | grep wikipedia-mcp
   ```

2. Restart Claude Desktop

3. Verify configuration:
   ```bash
   cat ~/.config/Claude/claude_desktop_config.json
   # or on macOS:
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

### Inaccurate Information

Wikipedia information may not always be current or accurate:

1. **Cross-reference**: Check official government sources
2. **Date awareness**: Wikipedia data has timestamps - check when it was last updated
3. **Multiple sources**: Use Wikipedia as one of several validation sources

### Rate Limiting

If you're making many Wikipedia queries:

1. **Batch requests**: Group related queries
2. **Cache results**: Store Wikipedia responses for reuse
3. **Respect limits**: Wikipedia has rate limits for API access

## Contributing Examples

Have you found a useful pattern for using Wikipedia MCP with this database? Please contribute!

1. Add your example to this file
2. Include the use case and expected outcome
3. Document any prerequisites
4. Submit a pull request

## Additional Resources

- [Wikipedia MCP Server Repository](https://github.com/rudra-ravi/wikipedia-mcp)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Wikipedia API Documentation](https://www.mediawiki.org/wiki/API:Main_page)
- [Countries States Cities Database Documentation](../README.md)
