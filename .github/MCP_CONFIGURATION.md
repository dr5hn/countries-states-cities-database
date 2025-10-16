# MCP Server Configuration for GitHub Copilot Agents

This repository is configured with Model Context Protocol (MCP) servers to enhance GitHub Copilot agents' ability to work with geographical data, validate information, and resolve issues efficiently.

## What is MCP?

Model Context Protocol (MCP) is a standardized way for AI assistants to access external tools and data sources. By configuring MCP servers, GitHub Copilot agents gain enhanced capabilities when working on issues in this repository.

## Configured MCP Servers

### 1. Wikipedia MCP Server
**Package**: `@modelcontextprotocol/server-wikipedia`  
**Purpose**: Access Wikipedia for geographical data validation

**Use Cases**:
- Validate country names, capitals, and administrative divisions
- Verify population figures and geographic coordinates
- Cross-reference timezone information
- Research historical city names and changes
- Get authoritative geographical context

**Example Queries**:
```
"What is the population of Mumbai according to Wikipedia?"
"Verify that Berlin is the capital of Germany"
"Get Wikipedia information about Tokyo's timezone"
```

### 2. Filesystem MCP Server
**Package**: `@modelcontextprotocol/server-filesystem`  
**Purpose**: Enhanced file system operations for large JSON files

**Use Cases**:
- Efficiently read and navigate large contribution JSON files
- Search across multiple city files simultaneously
- Batch edit operations on JSON data
- Fast file content inspection without loading entire files

**Example Operations**:
```
"Find all cities in contributions/cities/US.json with invalid timezones"
"Search for duplicate city IDs across all JSON files"
"List all states in contributions/states/states.json"
```

### 3. GitHub MCP Server
**Package**: `@modelcontextprotocol/server-github`  
**Purpose**: Access repository data and issue tracking

**Use Cases**:
- Read issue descriptions and requirements
- Check related pull requests and commit history
- Review previous fixes and patterns
- Access discussion threads and feedback
- Query repository structure and changes

**Example Queries**:
```
"Show me recent issues related to timezone fixes"
"Get the commit history for contributions/cities/JP.json"
"What changes were made in issue #1165?"
```

### 4. Brave Search MCP Server
**Package**: `@modelcontextprotocol/server-brave-search`  
**Purpose**: Web search for current and authoritative data

**Use Cases**:
- Find official government geographical data sources
- Verify current population statistics
- Search for timezone database updates
- Find authoritative sources for administrative divisions
- Research recent geographical changes (city renames, new states, etc.)

**Example Searches**:
```
"Official list of Japanese prefectures from government source"
"Current population of Delhi metropolitan area"
"IANA timezone database update for Egypt"
```

### 5. PostgreSQL MCP Server
**Package**: `@modelcontextprotocol/server-postgres`  
**Purpose**: Direct database access for queries and validation

**Use Cases**:
- Query existing data to understand structure
- Validate data before and after changes
- Check for duplicates and inconsistencies
- Generate statistics and counts
- Test data integrity

**Example Queries**:
```sql
"SELECT COUNT(*) FROM cities WHERE country_code = 'US'"
"Find cities with NULL timezone values"
"List all countries with missing capital cities"
```

## How These MCPs Help Resolve Data Issues

### Scenario 1: Adding New Cities
1. **Wikipedia MCP**: Verify city name, state, and coordinates
2. **Filesystem MCP**: Read existing state structure from JSON
3. **PostgreSQL MCP**: Check for duplicates and get next available ID
4. **GitHub MCP**: Reference similar issues and previous patterns
5. **Result**: Accurate, validated city data added efficiently

### Scenario 2: Fixing Timezone Data
1. **Brave Search MCP**: Find latest IANA timezone database
2. **Wikipedia MCP**: Verify city location and timezone
3. **PostgreSQL MCP**: Identify all cities with incorrect timezones
4. **Filesystem MCP**: Batch update JSON files
5. **Result**: Comprehensive timezone fix with validation

### Scenario 3: Validating Administrative Divisions
1. **Wikipedia MCP**: Get official list of states/provinces
2. **PostgreSQL MCP**: Query current database state
3. **GitHub MCP**: Check previous similar fixes
4. **Filesystem MCP**: Update contribution files
5. **Result**: Accurate administrative structure validated against authoritative sources

### Scenario 4: Removing Duplicate Entries
1. **PostgreSQL MCP**: Find duplicate cities by name and coordinates
2. **Filesystem MCP**: Identify source JSON files
3. **Wikipedia MCP**: Verify which entry is correct
4. **GitHub MCP**: Check if issue was reported before
5. **Result**: Duplicates removed with validation

## Configuration Details

### File Location
`.github/copilot-mcp.json`

### Environment Variables Required

Some MCP servers require environment variables:

- **GITHUB_TOKEN**: Automatically provided by GitHub Actions
- **BRAVE_API_KEY**: Optional, for Brave Search (get from https://brave.com/search/api/)

### How Copilot Agents Use These

When a GitHub Copilot agent works on an issue:

1. **Issue Analysis**: Uses GitHub MCP to read issue details
2. **Data Validation**: Uses Wikipedia and Brave Search for verification
3. **Code Navigation**: Uses Filesystem MCP to read/edit files efficiently
4. **Database Operations**: Uses PostgreSQL MCP for queries
5. **Pattern Recognition**: Uses GitHub MCP to learn from previous fixes

## Benefits for This Project

### Speed
- **Faster validation**: Instant Wikipedia lookups vs manual research
- **Efficient file operations**: Direct JSON access without loading entire files
- **Quick queries**: Database access without manual MySQL commands

### Accuracy
- **Authoritative sources**: Wikipedia and official data
- **Cross-validation**: Multiple sources confirm data
- **Pattern matching**: Learn from previous successful fixes

### Completeness
- **Comprehensive checks**: Search across all related data
- **Historical context**: Access previous issues and discussions
- **Related changes**: Identify all files that need updates

## Testing MCP Configuration

### Verify Configuration
```bash
cat .github/copilot-mcp.json | jq .
```

### Test Individual MCPs
The configuration is automatically loaded by GitHub Copilot agents when they work on issues. No manual testing is required.

### Validation Workflow
1. Copilot agent receives issue
2. Loads MCP configuration from `.github/copilot-mcp.json`
3. Uses appropriate MCP servers based on task
4. Validates data using multiple sources
5. Makes changes with high confidence

## MCP Server Maintenance

### Updating MCP Servers
MCP servers are loaded dynamically via `npx`, so they're always up to date. No maintenance required.

### Adding New MCP Servers
To add a new MCP server:

1. Edit `.github/copilot-mcp.json`
2. Add new server configuration:
```json
{
  "server-name": {
    "command": "npx",
    "args": ["-y", "@package/mcp-server"],
    "description": "What this server does"
  }
}
```
3. Commit the changes

### Available MCP Servers

Popular MCP servers that could be added:

- **@modelcontextprotocol/server-sqlite**: SQLite database access
- **@modelcontextprotocol/server-memory**: Persistent memory for context
- **@modelcontextprotocol/server-puppeteer**: Web scraping for official data
- **@modelcontextprotocol/server-sequential-thinking**: Enhanced reasoning
- **@modelcontextprotocol/server-time**: Date/time utilities

## Troubleshooting

### MCP Server Not Working
- Check that the package name is correct
- Verify environment variables are set
- Ensure npx has internet access

### Performance Issues
- Reduce number of active MCP servers if needed
- Use specific servers for specific tasks
- Cache repeated queries where possible

## Examples of MCP-Enhanced Workflows

### Example 1: Fixing Yemen Cities (Issue #1165)
```
Agent workflow with MCPs:
1. [GitHub MCP] Read issue #1165 details
2. [PostgreSQL MCP] Query current Yemen cities: COUNT(*) = 2,600+
3. [Wikipedia MCP] Verify Yemen has 21 governorates (not 2,600+ cities)
4. [Filesystem MCP] Read contributions/cities/YE.json
5. [Wikipedia MCP] Validate each city name and governorate
6. [PostgreSQL MCP] Check for duplicates
7. [Filesystem MCP] Update YE.json with correct data
8. [PostgreSQL MCP] Validate: COUNT(*) = ~100 (correct)
9. [GitHub MCP] Reference previous similar fixes
10. Complete fix in minutes instead of hours
```

### Example 2: Adding New Indian States
```
Agent workflow with MCPs:
1. [GitHub MCP] Understand issue requirements
2. [Wikipedia MCP] Get official list of Indian states and UTs
3. [Brave Search MCP] Find government source for verification
4. [PostgreSQL MCP] Check existing states in database
5. [Filesystem MCP] Read contributions/states/states.json
6. [Wikipedia MCP] Get details for each new state (capital, population, etc.)
7. [Filesystem MCP] Add new states to JSON
8. [PostgreSQL MCP] Validate additions
9. Result: Accurate, verified state data
```

### Example 3: Timezone Corrections
```
Agent workflow with MCPs:
1. [PostgreSQL MCP] Find cities with timezone = NULL or invalid
2. [Wikipedia MCP] For each city, get correct timezone
3. [Brave Search MCP] Verify against IANA timezone database
4. [Filesystem MCP] Update contribution JSON files
5. [PostgreSQL MCP] Validate all timezones are now correct
6. Result: Comprehensive timezone fix with validation
```

## Integration with Existing Workflows

### JSON-First Workflow
MCPs enhance the JSON-first workflow:
1. **Before**: Manually research data → Edit JSON → Hope it's correct
2. **With MCPs**: Wikipedia/Brave verify data → Edit JSON with confidence → PostgreSQL validates

### Validation Steps
MCPs automate validation:
1. **Before**: Manual SQL queries and spreadsheet comparisons
2. **With MCPs**: Automated queries across Wikipedia, database, and files

### Documentation
MCPs help generate documentation:
1. **Before**: Manual research and writing
2. **With MCPs**: Auto-gather information from GitHub, Wikipedia, and database

## Best Practices

### When to Use Each MCP

- **Wikipedia**: First source for geographical data validation
- **Filesystem**: Reading/editing contribution JSON files
- **GitHub**: Understanding issues, patterns, and history
- **Brave Search**: When Wikipedia isn't enough (government sources)
- **PostgreSQL**: Database queries, validation, and testing

### Combining MCPs

Most effective when used together:
```
Wikipedia (verify) → PostgreSQL (check current) → Filesystem (edit) → PostgreSQL (validate)
```

### Error Handling

If an MCP server fails:
1. Task can still be completed with other MCPs
2. Fallback to manual verification if needed
3. Document any issues for troubleshooting

## Future Enhancements

Potential additions:
- Custom MCP server for IANA timezone database
- Custom MCP server for GeoNames.org
- Custom MCP server for country code standards (ISO 3166)
- Integration with government API endpoints
- Cached Wikipedia data for offline access

## Contributing

To improve MCP configuration:
1. Identify useful MCP servers for geographical data
2. Test configuration with sample issues
3. Update `.github/copilot-mcp.json`
4. Document use cases in this file
5. Submit pull request

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- [GitHub Copilot MCP Integration](https://docs.github.com/en/copilot)
- [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page)
- [IANA Timezone Database](https://www.iana.org/time-zones)

---

**Last Updated**: October 2025  
**Configuration Version**: 1.0.0  
**Maintained By**: Countries States Cities Database project
