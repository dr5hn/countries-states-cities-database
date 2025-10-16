# Wikipedia MCP Integration Architecture

## System Overview

This document describes the architecture of the Wikipedia MCP integration with the Countries States Cities Database.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        User / Developer                              │
│                                                                       │
│  Interacts via:                                                      │
│  • Claude Desktop (AI Assistant)                                     │
│  • Command Line (scripts)                                            │
│  • Database queries                                                   │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         │ Natural Language Queries
                         │ "Tell me about Tokyo using Wikipedia"
                         │
┌────────────────────────▼──────────────────────────────────────────┐
│                    Claude Desktop                                   │
│                  (AI Assistant with MCP)                            │
│                                                                     │
│  Capabilities:                                                      │
│  • Process natural language                                         │
│  • Route queries to appropriate MCP servers                         │
│  • Combine multiple data sources                                    │
│  • Format responses                                                 │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         │ MCP Protocol
                         │ (Structured API calls)
                         │
┌────────────────────────▼──────────────────────────────────────────┐
│              Wikipedia MCP Server                                   │
│              (wikipedia-mcp package)                                │
│                                                                     │
│  Installation:                                                      │
│  • Via pipx: ~/.local/bin/wikipedia-mcp                            │
│  • Via venv: ./mcp/venv/bin/wikipedia-mcp                          │
│                                                                     │
│  Tools Provided:                                                    │
│  • search_wikipedia - Search for articles                           │
│  • get_summary - Get article summaries                              │
│  • get_content - Get full article content                           │
│  • get_sections - Get specific sections                             │
│  • get_links - Find related articles                                │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         │ Wikipedia API (MediaWiki)
                         │ HTTP/HTTPS requests
                         │
┌────────────────────────▼──────────────────────────────────────────┐
│                      Wikipedia                                      │
│                  (External Data Source)                             │
│                                                                     │
│  Data Available:                                                    │
│  • Articles (6M+ in English)                                        │
│  • Infoboxes with structured data                                   │
│  • Historical information                                           │
│  • Geographic data                                                  │
│  • Cultural context                                                 │
│  • Population figures                                               │
│  • Administrative divisions                                         │
└─────────────────────────────────────────────────────────────────────┘


                  ┌───────────────────────────────────┐
                  │   Integration with Database       │
                  └───────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│               Countries States Cities Database                       │
│                                                                       │
│  Components:                                                          │
│  ├── MySQL Database (world.sql)                                      │
│  │   └── Tables: countries, states, cities                           │
│  ├── JSON Files (contributions/)                                     │
│  │   └── Source of truth for data                                    │
│  └── Export Formats                                                  │
│      ├── JSON, CSV, XML, YAML                                        │
│      ├── MongoDB                                                     │
│      └── SQL (MySQL, PostgreSQL, SQL Server, SQLite)                 │
└─────────────────────────────────────────────────────────────────────┘
                         │
                         │ Validation & Enrichment
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Workflow Examples                                 │
│                                                                       │
│  1. Data Validation:                                                 │
│     MySQL Query → Claude + Wikipedia MCP → Verify → Update JSON      │
│                                                                       │
│  2. Data Enrichment:                                                 │
│     Identify Gaps → Claude + Wikipedia MCP → Extract Info → Add      │
│                                                                       │
│  3. Research:                                                        │
│     Query Topic → Claude + Wikipedia MCP → Analyze → Document        │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Query Flow

```
User Query
    │
    ├─→ "Tell me about Tokyo using Wikipedia"
    │
    ▼
Claude Desktop (receives query)
    │
    ├─→ Recognizes "Wikipedia" keyword
    │
    ▼
Wikipedia MCP Server
    │
    ├─→ Calls MediaWiki API
    │
    ▼
Wikipedia API
    │
    ├─→ Returns article data
    │
    ▼
Wikipedia MCP Server
    │
    ├─→ Formats response for MCP
    │
    ▼
Claude Desktop
    │
    ├─→ Processes and formats for user
    │
    ▼
User (receives formatted response)
```

### Validation Workflow

```
Database Entry
    │
    ├─→ SELECT * FROM cities WHERE name='Tokyo'
    │   Result: {name: 'Tokyo', country_code: 'JP', timezone: 'Asia/Tokyo'}
    │
    ▼
User asks Claude
    │
    ├─→ "Verify Tokyo's timezone using Wikipedia"
    │
    ▼
Claude + Wikipedia MCP
    │
    ├─→ Searches Wikipedia for Tokyo
    ├─→ Extracts timezone information
    │   Result: "Asia/Tokyo (UTC+9)"
    │
    ▼
Comparison
    │
    ├─→ Database: Asia/Tokyo
    ├─→ Wikipedia: Asia/Tokyo
    │   Status: ✅ Match
    │
    ▼
User informed (data validated)
```

### Enrichment Workflow

```
Database Entry (sparse)
    │
    ├─→ {name: 'Paris', country_code: 'FR', timezone: 'Europe/Paris'}
    │   Missing: population, historical_name, description
    │
    ▼
User asks Claude
    │
    ├─→ "Get additional information about Paris from Wikipedia"
    │
    ▼
Claude + Wikipedia MCP
    │
    ├─→ Retrieves Wikipedia article
    ├─→ Extracts relevant sections
    │   • Population: ~2.2M (city), ~12M (metro)
    │   • Historical names: Lutetia (Roman)
    │   • Description: "Capital of France..."
    │
    ▼
User reviews enriched data
    │
    ├─→ Decides to add to database
    │
    ▼
Update JSON files
    │
    ├─→ contributions/cities/FR.json
    │
    ▼
Sync to database
    │
    ├─→ python3 bin/scripts/sync/import_json_to_mysql.py
    │
    ▼
Database updated with enriched data
```

## Component Details

### 1. Installation Methods

#### Method A: pipx (Global)
```bash
pipx install git+https://github.com/rudra-ravi/wikipedia-mcp.git
# Installs to: ~/.local/bin/wikipedia-mcp
# Pros: Available system-wide, isolated
# Cons: Requires pipx
```

#### Method B: Virtual Environment (Local)
```bash
cd mcp
python3 -m venv venv
source venv/bin/activate
pip install git+https://github.com/rudra-ravi/wikipedia-mcp.git
# Installs to: ./mcp/venv/bin/wikipedia-mcp
# Pros: Project-specific, no system dependencies
# Cons: Must activate venv
```

### 2. Configuration

#### Claude Desktop Config Structure
```json
{
  "mcpServers": {
    "wikipedia": {
      "command": "wikipedia-mcp"  // or full path
    }
  }
}
```

#### Config Locations by OS
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

### 3. MCP Protocol Communication

```
Claude Desktop                Wikipedia MCP Server
      │                              │
      ├──────(Request)──────────────→│
      │  {                           │
      │    "method": "search",       │
      │    "params": {               │
      │      "query": "Tokyo"        │
      │    }                         │
      │  }                           │
      │                              │
      │←────(Response)────────────────┤
      │  {                           │
      │    "result": {               │
      │      "title": "Tokyo",       │
      │      "summary": "...",       │
      │      "url": "..."            │
      │    }                         │
      │  }                           │
      │                              │
```

## Security Considerations

### Network Security
- All Wikipedia API calls are HTTPS
- No sensitive data transmitted
- Rate limiting applied by Wikipedia

### Local Security
- MCP server runs locally (no remote execution)
- No database credentials exposed to Wikipedia
- Read-only access to Wikipedia

### Data Privacy
- Queries to Wikipedia are logged by Wikimedia Foundation (their privacy policy applies)
- No database data sent to Wikipedia unless explicitly requested by user
- MCP communication is local (Claude ↔ MCP server)

## Performance

### Caching
- Wikipedia MCP server may implement local caching (check package docs)
- Claude Desktop may cache MCP responses
- Browser caching if using web interface

### Rate Limiting
- Wikipedia API: ~200 requests/second (reasonable use)
- Recommendation: Batch queries, don't spam
- MCP server handles rate limiting

### Latency
- Local (Claude ↔ MCP): < 1ms
- Network (MCP ↔ Wikipedia): 100-500ms (depends on location)
- Total response time: 1-3 seconds typical

## Scalability

### Single User
- Perfect for interactive use
- No scaling concerns

### Multiple Users / Automation
- Consider:
  - Implementing caching layer
  - Rate limiting at application level
  - Batch processing for large datasets
  - Respect Wikipedia's usage policies

## Monitoring and Debugging

### Check MCP Server Status
```bash
# If using pipx
which wikipedia-mcp
wikipedia-mcp --version  # (if supported)

# If using venv
source mcp/venv/bin/activate
which wikipedia-mcp
```

### Claude Desktop Logs
- Check Claude Desktop's console/logs for MCP errors
- Restart Claude Desktop if MCP stops responding

### Wikipedia API Status
- Check: https://www.wikitech.wikimedia.org/wiki/Incident_status
- Monitor for API outages

## Extension Points

### Future Enhancements

1. **Custom MCP Tools**
   - Add database-specific MCP tools
   - Direct SQL query tools
   - Batch validation tools

2. **Automated Pipelines**
   - Scheduled validation jobs
   - Automatic enrichment scripts
   - Conflict detection automation

3. **Multi-Language Support**
   - Query Wikipedia in different languages
   - Cross-reference translations

4. **Integration with Exports**
   - Add Wikipedia links to exports
   - Include enriched descriptions
   - Generate documentation automatically

## Troubleshooting Architecture

### Issue: MCP Server Not Found

```
User → Claude Desktop → (ERROR: wikipedia-mcp not found)

Solutions:
1. Check PATH: echo $PATH
2. Verify install: which wikipedia-mcp
3. Check config: correct path in claude_desktop_config.json
4. Reinstall: bash mcp/install.sh
```

### Issue: No Wikipedia Data

```
User → Claude Desktop → Wikipedia MCP → (ERROR: Connection failed)

Solutions:
1. Check internet: ping wikipedia.org
2. Check API status: visit wikipedia.org
3. Check firewall: allow HTTPS to wikipedia.org
4. Try different query: "search Wikipedia for Tokyo"
```

### Issue: Slow Responses

```
User → Claude Desktop → Wikipedia MCP → Wikipedia API (SLOW)

Solutions:
1. Check network latency: ping wikipedia.org
2. Reduce query complexity: ask for summaries instead of full articles
3. Check Wikipedia API status
4. Consider implementing local caching
```

## Maintenance

### Updates
```bash
# Update Wikipedia MCP server
pipx upgrade wikipedia-mcp
# or
source mcp/venv/bin/activate
pip install --upgrade git+https://github.com/rudra-ravi/wikipedia-mcp.git
```

### Backups
- Claude Desktop config: Backup before changes
- MCP configurations: Version controlled in this repo

### Health Checks
```bash
# Test Wikipedia MCP
# In Claude Desktop: "Tell me about London using Wikipedia"
# Expected: Article summary about London, England
```

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Maintained By**: Countries States Cities Database project
