# Testing the Wikipedia MCP Integration

This guide helps you verify that the Wikipedia MCP integration is working correctly.

## Pre-Installation Tests

### Test 1: Python Version
```bash
python3 --version
# Expected: Python 3.8.0 or higher
```

### Test 2: Internet Connectivity
```bash
ping -c 3 wikipedia.org
# Expected: Successful ping responses
```

### Test 3: Claude Desktop Installation
Check that Claude Desktop is installed and can be launched.

## Installation Tests

### Test 4: Installation Script Syntax
```bash
cd /path/to/countries-states-cities-database
bash -n mcp/install.sh
# Expected: No output (means syntax is OK)
```

### Test 5: Configuration Script Syntax
```bash
bash -n mcp/generate_config.sh
# Expected: No output (means syntax is OK)
```

### Test 6: JSON Configuration Validity
```bash
python3 -m json.tool mcp/claude_desktop_config.example.json
# Expected: Pretty-printed JSON output
```

## Post-Installation Tests

### Test 7: pipx Installation Verification
If you installed using pipx:
```bash
pipx list | grep wikipedia-mcp
# Expected: wikipedia-mcp package listed

which wikipedia-mcp
# Expected: /home/username/.local/bin/wikipedia-mcp
```

### Test 8: Virtual Environment Installation Verification
If you installed using virtual environment:
```bash
source mcp/venv/bin/activate
which wikipedia-mcp
# Expected: /path/to/mcp/venv/bin/wikipedia-mcp

wikipedia-mcp --help 2>&1 | head -5
# Expected: Help text or error message (means it's installed)
```

### Test 9: Configuration File Created
```bash
# For macOS
ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json

# For Linux
ls -la ~/.config/Claude/claude_desktop_config.json

# Expected: File exists and contains "wikipedia" entry
```

### Test 10: Configuration File Validity
```bash
# For macOS
python3 -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

# For Linux
python3 -m json.tool ~/.config/Claude/claude_desktop_config.json

# Expected: Valid JSON with "mcpServers" and "wikipedia" entries
```

## Integration Tests

### Test 11: Simple Wikipedia Query
**Open Claude Desktop and try:**
```
Tell me about London using Wikipedia
```

**Expected Response:**
- Information about London, England
- Capital of the United Kingdom
- Population, geography, history details
- No errors about "Wikipedia MCP not found"

**Pass Criteria:**
✅ Response contains Wikipedia information
✅ No MCP errors
✅ Response is relevant to London

### Test 12: Specific Information Retrieval
**In Claude Desktop:**
```
What does Wikipedia say is the capital of Japan?
```

**Expected Response:**
- "Tokyo" or "Tokyo is the capital of Japan"
- Information sourced from Wikipedia

**Pass Criteria:**
✅ Correct answer (Tokyo)
✅ Information attributed to Wikipedia
✅ No errors

### Test 13: Multiple Location Query
**In Claude Desktop:**
```
Get Wikipedia summaries for Paris, London, and Berlin
```

**Expected Response:**
- Information about all three cities
- Brief summary for each
- Organized presentation

**Pass Criteria:**
✅ Information for all three cities
✅ Data from Wikipedia
✅ Clear, structured response

### Test 14: Database Validation Query
**First, get data from database:**
```bash
mysql -uroot -proot -e "SELECT name, country_code, timezone FROM world.cities WHERE name='Tokyo' LIMIT 1;" 2>/dev/null
```

**Then in Claude Desktop:**
```
I have Tokyo in my database with timezone "Asia/Tokyo".
Can you verify this is correct using Wikipedia?
```

**Expected Response:**
- Confirmation or correction
- Wikipedia-based verification
- Timezone information from Wikipedia

**Pass Criteria:**
✅ Validates timezone information
✅ Uses Wikipedia as source
✅ Provides clear yes/no answer

### Test 15: Enrichment Query
**In Claude Desktop:**
```
Using Wikipedia, give me a one-sentence description of Mumbai, India
```

**Expected Response:**
- Single sentence description
- Factual information
- Sourced from Wikipedia

**Pass Criteria:**
✅ One-sentence format
✅ Relevant information about Mumbai
✅ Based on Wikipedia data

## Error Handling Tests

### Test 16: Non-Existent Location
**In Claude Desktop:**
```
Tell me about the city of Atlantis using Wikipedia
```

**Expected Response:**
- Information about Atlantis (mythical city)
- Or message that it's not a real location
- Graceful handling

**Pass Criteria:**
✅ No crash or error
✅ Reasonable response
✅ Handles ambiguity

### Test 17: Ambiguous Query
**In Claude Desktop:**
```
What does Wikipedia say about Paris?
```

**Expected Response:**
- Should assume Paris, France (most common)
- Or ask for clarification
- Provides relevant information

**Pass Criteria:**
✅ Handles ambiguity well
✅ Provides useful information
✅ No errors

### Test 18: Offline Test
**Disconnect from internet, then in Claude Desktop:**
```
Tell me about Rome using Wikipedia
```

**Expected Response:**
- Error message about connectivity
- Or graceful failure message
- No crash

**Pass Criteria:**
✅ Handles offline gracefully
✅ Clear error message
✅ Doesn't crash Claude Desktop

## Performance Tests

### Test 19: Response Time
**In Claude Desktop:**
```
Tell me about Sydney, Australia using Wikipedia
```

**Measure time from Enter to response.**

**Expected:**
- First response: 2-5 seconds
- Follow-up queries: 1-3 seconds

**Pass Criteria:**
✅ Response within 10 seconds
✅ Reasonable latency
✅ Complete information provided

### Test 20: Multiple Rapid Queries
**In Claude Desktop, send these quickly:**
```
1. Tell me about Tokyo using Wikipedia
2. Tell me about Beijing using Wikipedia  
3. Tell me about Seoul using Wikipedia
```

**Expected:**
- All three queries answered
- No rate limiting errors
- Consistent response quality

**Pass Criteria:**
✅ All queries answered
✅ No errors
✅ Reasonable performance

## Integration with Database Tests

### Test 21: Country Validation
**Query database:**
```bash
mysql -uroot -proot -e "SELECT name FROM world.countries WHERE iso2='DE' LIMIT 1;" 2>/dev/null
```

**In Claude Desktop:**
```
What does Wikipedia list as the official name of Germany?
Verify it matches: [paste database result]
```

**Pass Criteria:**
✅ Verifies country name
✅ Uses Wikipedia
✅ Provides comparison

### Test 22: State/Province Validation
**Query database:**
```bash
mysql -uroot -proot -e "SELECT name FROM world.states WHERE country_code='US' AND name LIKE 'Calif%';" 2>/dev/null
```

**In Claude Desktop:**
```
According to Wikipedia, what is the full name of the US state abbreviated as CA?
```

**Pass Criteria:**
✅ Returns "California"
✅ Uses Wikipedia source
✅ Accurate information

### Test 23: City Population Verification
**Query database:**
```bash
mysql -uroot -proot -e "SELECT name, country_code FROM world.cities WHERE name='Mumbai';" 2>/dev/null
```

**In Claude Desktop:**
```
What is Mumbai's population according to Wikipedia?
```

**Pass Criteria:**
✅ Provides population figure
✅ Cites Wikipedia
✅ Includes year/context

## Advanced Tests

### Test 24: Batch Validation
**In Claude Desktop:**
```
Using Wikipedia, verify these capital cities:
- France: Paris
- Germany: Berlin
- Italy: Rome
- Spain: Madrid
- Japan: Tokyo

Are all correct?
```

**Pass Criteria:**
✅ Verifies all five
✅ Confirms correctness
✅ Notes any discrepancies

### Test 25: Historical Information
**In Claude Desktop:**
```
What was Istanbul called historically according to Wikipedia?
```

**Expected Response:**
- Constantinople
- Byzantium
- Historical context

**Pass Criteria:**
✅ Provides historical names
✅ From Wikipedia
✅ Accurate information

### Test 26: Administrative Divisions
**In Claude Desktop:**
```
According to Wikipedia, how many states does Germany have?
List them.
```

**Expected Response:**
- 16 states (Bundesländer)
- List of all states

**Pass Criteria:**
✅ Correct count (16)
✅ Lists all states
✅ From Wikipedia

## Troubleshooting Tests

### Test 27: Configuration Validation
```bash
# Generate fresh config
bash mcp/generate_config.sh

# Verify output
cat mcp/claude_desktop_config.json
```

**Pass Criteria:**
✅ Valid JSON
✅ Contains "wikipedia" entry
✅ Correct command path

### Test 28: Installation Reinstall
```bash
# If using pipx
pipx uninstall wikipedia-mcp
pipx install git+https://github.com/rudra-ravi/wikipedia-mcp.git

# If using venv
rm -rf mcp/venv
bash mcp/install.sh
```

**Pass Criteria:**
✅ Reinstalls successfully
✅ No errors
✅ Still works in Claude Desktop

### Test 29: Log Inspection
Check Claude Desktop logs for MCP-related messages.

**Look for:**
- MCP server initialization
- Wikipedia MCP connection status
- Any error messages

**Pass Criteria:**
✅ MCP server starts
✅ Wikipedia connection successful
✅ No persistent errors

## Test Results Summary

Use this checklist to track your test results:

### Pre-Installation
- [ ] Test 1: Python Version
- [ ] Test 2: Internet Connectivity
- [ ] Test 3: Claude Desktop Installation

### Installation
- [ ] Test 4: Install Script Syntax
- [ ] Test 5: Config Script Syntax
- [ ] Test 6: JSON Validity

### Post-Installation
- [ ] Test 7: pipx Verification (if applicable)
- [ ] Test 8: Venv Verification (if applicable)
- [ ] Test 9: Config File Created
- [ ] Test 10: Config File Validity

### Integration
- [ ] Test 11: Simple Wikipedia Query
- [ ] Test 12: Specific Information
- [ ] Test 13: Multiple Locations
- [ ] Test 14: Database Validation
- [ ] Test 15: Enrichment Query

### Error Handling
- [ ] Test 16: Non-Existent Location
- [ ] Test 17: Ambiguous Query
- [ ] Test 18: Offline Handling

### Performance
- [ ] Test 19: Response Time
- [ ] Test 20: Multiple Rapid Queries

### Database Integration
- [ ] Test 21: Country Validation
- [ ] Test 22: State Validation
- [ ] Test 23: City Population

### Advanced
- [ ] Test 24: Batch Validation
- [ ] Test 25: Historical Information
- [ ] Test 26: Administrative Divisions

### Troubleshooting
- [ ] Test 27: Configuration Validation
- [ ] Test 28: Reinstallation
- [ ] Test 29: Log Inspection

## Reporting Issues

If tests fail, collect the following information:

1. **Test number** that failed
2. **Expected result** vs **Actual result**
3. **Error messages** (full text)
4. **System information**:
   ```bash
   uname -a
   python3 --version
   pipx --version  # if using pipx
   ```
5. **Configuration**:
   ```bash
   cat ~/.config/Claude/claude_desktop_config.json
   # or macOS equivalent
   ```

Submit issues to: https://github.com/dr5hn/countries-states-cities-database/issues

## Continuous Testing

### Weekly Checks
- Test 11: Simple Wikipedia Query
- Test 14: Database Validation Query

### Monthly Checks
- Test 7/8: Installation Verification
- Test 24: Batch Validation
- Test 19: Response Time

### After Updates
- Run all Installation Tests (4-6)
- Run all Post-Installation Tests (7-10)
- Run key Integration Tests (11, 14, 15)

## Success Criteria

The integration is considered successful if:

✅ **Core Tests Pass**: Tests 11-15 all pass  
✅ **Performance Acceptable**: Test 19 shows < 10s response time  
✅ **Error Handling Works**: Tests 16-18 show graceful handling  
✅ **Database Integration**: Tests 21-23 verify database correctly

---

**Testing Version**: 1.0.0  
**Last Updated**: October 2025  
**Maintained By**: Countries States Cities Database project
