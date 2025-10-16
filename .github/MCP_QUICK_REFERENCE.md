# MCP Quick Reference for Copilot Agents

This is a quick reference guide for GitHub Copilot agents working on data-related issues in the Countries States Cities Database.

## Available MCP Servers

| MCP Server | Primary Use | Quick Example |
|------------|-------------|---------------|
| **Wikipedia** | Validate geographical data | "What is Tokyo's population per Wikipedia?" |
| **Filesystem** | Read/edit JSON files | "Read contributions/cities/US.json" |
| **GitHub** | Access issues & history | "Show commits for issue #1165" |
| **Brave Search** | Find official sources | "Search for official list of German states" |
| **PostgreSQL** | Query database | "SELECT COUNT(*) FROM cities WHERE country_code='JP'" |

## Common Workflows

### 1. Validating City Data
```
Step 1: [GitHub MCP] Read issue requirements
Step 2: [PostgreSQL MCP] Query current database state
Step 3: [Wikipedia MCP] Verify city information
Step 4: [Filesystem MCP] Edit contribution JSON
Step 5: [PostgreSQL MCP] Validate changes
```

### 2. Adding New States/Provinces
```
Step 1: [Wikipedia MCP] Get official list of subdivisions
Step 2: [Brave Search MCP] Verify with government source
Step 3: [PostgreSQL MCP] Check existing data
Step 4: [Filesystem MCP] Read/update states.json
Step 5: [PostgreSQL MCP] Validate additions
```

### 3. Fixing Timezone Issues
```
Step 1: [PostgreSQL MCP] Find cities with invalid timezones
Step 2: [Wikipedia MCP] Get correct timezone for each city
Step 3: [Filesystem MCP] Update contribution files
Step 4: [PostgreSQL MCP] Verify all timezones correct
```

### 4. Removing Duplicates
```
Step 1: [PostgreSQL MCP] Find duplicate entries
Step 2: [Wikipedia MCP] Determine which is correct
Step 3: [Filesystem MCP] Remove duplicates from JSON
Step 4: [PostgreSQL MCP] Confirm no duplicates remain
```

## MCP Server Capabilities

### Wikipedia MCP
**What it does**: Access Wikipedia articles and data

**Key functions**:
- Search for articles
- Get article summaries
- Extract specific sections
- Get infobox data
- Find related articles

**Best for**:
- Country/city/state validation
- Population figures
- Administrative divisions
- Geographic coordinates
- Historical information

### Filesystem MCP
**What it does**: Enhanced file operations

**Key functions**:
- Read file contents
- Write to files
- Search within files
- List directory contents
- Batch operations

**Best for**:
- Reading contribution JSON files
- Editing large data files
- Searching across multiple files
- Batch updates

### GitHub MCP
**What it does**: Access GitHub repository data

**Key functions**:
- Read issues and PRs
- View commit history
- Search code and discussions
- Access file changes
- Query repository structure

**Best for**:
- Understanding issue context
- Learning from previous fixes
- Finding related changes
- Reviewing patterns

### Brave Search MCP
**What it does**: Web search with API

**Key functions**:
- Search the web
- Find official sources
- Get current information
- Verify data accuracy

**Best for**:
- Government data sources
- Official statistics
- Recent changes
- Authoritative references

### PostgreSQL MCP
**What it does**: Direct database access

**Key functions**:
- Run SQL queries
- Check data integrity
- Get statistics
- Validate changes
- Test data

**Best for**:
- Current data state
- Duplicate detection
- Count validation
- Structure verification

## Quick Commands by Task

### Task: Validate a Country's Capital
```
[Wikipedia MCP] "What is the capital of Germany?"
[PostgreSQL MCP] "SELECT capital FROM countries WHERE name='Germany'"
Compare results → Update if needed
```

### Task: Check City Count for Country
```
[PostgreSQL MCP] "SELECT COUNT(*) FROM cities WHERE country_code='US'"
[Wikipedia MCP] "How many cities does the United States have?"
Analyze discrepancy → Investigate
```

### Task: Verify State Names
```
[Wikipedia MCP] "List all states of India"
[PostgreSQL MCP] "SELECT name FROM states WHERE country_code='IN'"
[Brave Search MCP] "Official list of Indian states government"
Cross-reference → Update if needed
```

### Task: Find Cities with Missing Timezones
```
[PostgreSQL MCP] "SELECT name, country_code FROM cities WHERE timezone IS NULL LIMIT 100"
For each city:
  [Wikipedia MCP] "What is the timezone of {city}, {country}?"
  [Filesystem MCP] Update JSON file
```

### Task: Research Administrative Structure
```
[Wikipedia MCP] "Administrative divisions of Japan"
[Brave Search MCP] "Official Japanese prefecture list"
[PostgreSQL MCP] "SELECT COUNT(*) FROM states WHERE country_code='JP'"
Validate structure
```

## Error Handling

### If Wikipedia MCP Fails
- Use Brave Search MCP for web search
- Check official government sources
- Cross-reference with multiple sources

### If Filesystem MCP Fails
- Use standard file operations
- Break large files into chunks
- Handle JSON parsing separately

### If PostgreSQL MCP Fails
- Check database connection
- Use MySQL command line as fallback
- Verify database is running

### If GitHub MCP Fails
- Read issue directly from UI
- Check GitHub status page
- Use git commands as fallback

### If Brave Search MCP Fails
- Use Wikipedia MCP only
- Manual web research if needed
- Document source limitations

## Best Practices

### 1. Always Validate with Multiple Sources
✅ Good: Wikipedia + Brave Search + PostgreSQL
❌ Bad: Single source without verification

### 2. Use Appropriate MCP for Task
✅ Good: PostgreSQL for counts, Wikipedia for validation
❌ Bad: Wikipedia for everything

### 3. Combine MCPs for Complex Tasks
✅ Good: GitHub (context) → Wikipedia (validate) → PostgreSQL (check) → Filesystem (edit)
❌ Bad: Using only one MCP

### 4. Document Sources
✅ Good: "Per Wikipedia [link] and government source [link]"
❌ Bad: "I found that..."

### 5. Verify Before Committing
✅ Good: PostgreSQL query confirms change is correct
❌ Bad: Assume change is correct

## Performance Tips

### Efficient Wikipedia Queries
- Be specific: "Population of Tokyo" not "Tokyo"
- Batch similar queries when possible
- Cache results for repeated lookups

### Efficient Database Queries
- Use WHERE clauses to limit results
- Get counts before full data
- Use indexes (country_code, state_code)

### Efficient File Operations
- Read only necessary sections
- Use search instead of reading entire file
- Batch edits when possible

## Common Patterns

### Pattern 1: Fix Wrong Data
1. Identify issue → [GitHub MCP]
2. Find wrong entries → [PostgreSQL MCP]
3. Get correct data → [Wikipedia MCP]
4. Update files → [Filesystem MCP]
5. Validate fix → [PostgreSQL MCP]

### Pattern 2: Add Missing Data
1. Identify what's missing → [PostgreSQL MCP]
2. Research correct data → [Wikipedia MCP] + [Brave Search MCP]
3. Update contribution files → [Filesystem MCP]
4. Verify additions → [PostgreSQL MCP]

### Pattern 3: Remove Invalid Data
1. Find invalid entries → [PostgreSQL MCP]
2. Verify they're invalid → [Wikipedia MCP]
3. Remove from files → [Filesystem MCP]
4. Confirm removal → [PostgreSQL MCP]

### Pattern 4: Restructure Data
1. Understand requirement → [GitHub MCP]
2. Analyze current structure → [PostgreSQL MCP]
3. Research correct structure → [Wikipedia MCP]
4. Plan changes → Document
5. Execute changes → [Filesystem MCP]
6. Validate → [PostgreSQL MCP]

## Troubleshooting

### Issue: Can't Find City in Wikipedia
**Solution**: Try Brave Search for official government sources

### Issue: Database Query Returns Unexpected Results
**Solution**: Verify database is seeded correctly, check table structure

### Issue: JSON File Too Large to Edit
**Solution**: Use Filesystem MCP to edit specific sections

### Issue: Conflicting Information
**Solution**: Prioritize: Government source > Wikipedia > Other sources

### Issue: MCP Server Not Responding
**Solution**: Check network, verify configuration, try alternative MCP

## Resources

- **MCP Configuration**: `.github/copilot-mcp.json`
- **Full Documentation**: `.github/MCP_CONFIGURATION.md`
- **Contribution Guidelines**: `contributions/` JSON files
- **Database Schema**: `sql/world.sql`
- **Sync Scripts**: `bin/scripts/sync/`

## Quick Validation Checklist

Before committing changes:

- [ ] Validated with Wikipedia or authoritative source
- [ ] Checked database before changes (count/structure)
- [ ] Updated contribution JSON files
- [ ] Verified changes in database (count/structure match)
- [ ] No duplicate entries created
- [ ] All required fields present
- [ ] Followed existing data patterns
- [ ] Documented sources in commit/PR

---

**Last Updated**: October 2025  
**Version**: 1.0.0  
**For**: GitHub Copilot Agents working on data issues
