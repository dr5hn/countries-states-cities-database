# Quick Start Guide - Wikipedia MCP Integration

Get up and running with Wikipedia MCP in under 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Claude Desktop installed
- 5 minutes of your time

## Step 1: Install the Wikipedia MCP Server (2 minutes)

### Option A: Using pipx (Recommended)

```bash
# Install pipx if not already installed
sudo apt install pipx  # Linux
# or
brew install pipx      # macOS

# Configure path
pipx ensurepath

# Install Wikipedia MCP server
pipx install git+https://github.com/rudra-ravi/wikipedia-mcp.git
```

### Option B: Use Our Installation Script

```bash
# From the project root directory
cd /path/to/countries-states-cities-database
bash mcp/install.sh
```

Follow the prompts and choose your preferred installation method.

## Step 2: Configure Claude Desktop (2 minutes)

### Automatic Configuration

```bash
# Generate and install configuration
bash mcp/generate_config.sh
```

The script will:
1. Detect your installation method
2. Generate the appropriate configuration
3. Offer to install it automatically

### Manual Configuration

If you prefer to configure manually:

1. Locate your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

2. Add this configuration:

```json
{
  "mcpServers": {
    "wikipedia": {
      "command": "wikipedia-mcp"
    }
  }
}
```

3. If the file already exists, add the `"wikipedia"` entry under `"mcpServers"`

## Step 3: Restart Claude Desktop (30 seconds)

1. Quit Claude Desktop completely
2. Start Claude Desktop again
3. Wait for it to fully load

## Step 4: Test the Integration (30 seconds)

Open Claude Desktop and try one of these prompts:

### Test 1: Simple Query
```
Tell me about Tokyo, Japan using Wikipedia information
```

### Test 2: Database Validation
```
What does Wikipedia say about the capital of France?
```

### Test 3: Multiple Locations
```
Get Wikipedia summaries for London, Paris, and Berlin
```

If Claude responds with Wikipedia information, you're all set! 🎉

## What's Next?

### For This Project

Now you can use Wikipedia information to:

1. **Validate database entries**
   ```
   My database shows Berlin is the capital of Germany.
   Can you verify this using Wikipedia?
   ```

2. **Enrich data**
   ```
   Get population and area information from Wikipedia for:
   - Tokyo, Japan
   - Delhi, India
   - Shanghai, China
   ```

3. **Research locations**
   ```
   Using Wikipedia, tell me about the history and significance of:
   - Mumbai, India
   - São Paulo, Brazil
   - Lagos, Nigeria
   ```

### Example Workflows

#### Workflow 1: Validate a Country's States

```bash
# 1. Query database
mysql -uroot -proot -e "SELECT name FROM world.states WHERE country_code='US' ORDER BY name;"

# 2. Ask Claude (in Claude Desktop)
# "Using Wikipedia, list all US states. Compare with this database list: [paste results]"

# 3. Fix any discrepancies in contributions/states/states.json
```

#### Workflow 2: Enrich City Information

```bash
# 1. Identify cities needing context
mysql -uroot -proot -e "SELECT name, country_code FROM world.cities WHERE country_code='JP' LIMIT 10;"

# 2. Ask Claude
# "For each of these Japanese cities, get a one-sentence description from Wikipedia: [paste list]"

# 3. Use the information to enhance documentation
```

#### Workflow 3: Verify Timezone Data

```bash
# 1. Check a city's timezone
mysql -uroot -proot -e "SELECT name, timezone FROM world.cities WHERE name='Sydney' AND country_code='AU';"

# 2. Ask Claude
# "What timezone does Wikipedia list for Sydney, Australia?"

# 3. Update if needed in contributions/cities/AU.json
```

## Troubleshooting

### "Wikipedia MCP not found" error

**Solution**:
```bash
# If using pipx
pipx ensurepath
source ~/.bashrc  # or ~/.zshrc

# If using virtual environment
cd mcp
source venv/bin/activate
which wikipedia-mcp  # This is the path to use in config
```

### Claude doesn't seem to use Wikipedia

**Solution**:
1. Check configuration file exists and is valid JSON
2. Ensure you restarted Claude Desktop after adding config
3. Try explicitly asking: "Use Wikipedia to tell me about..."

### Permission denied when running scripts

**Solution**:
```bash
chmod +x mcp/install.sh
chmod +x mcp/generate_config.sh
```

### Python version too old

**Solution**:
```bash
# Check your Python version
python3 --version

# If < 3.8, upgrade Python
# Ubuntu/Debian
sudo apt update && sudo apt install python3.10

# macOS
brew install python@3.10
```

## Getting Help

- **Documentation**: See [mcp/README.md](README.md) for detailed information
- **Examples**: See [mcp/EXAMPLES.md](EXAMPLES.md) for usage examples
- **Issues**: Report problems in the GitHub Issues section
- **Community**: Join our Discord for real-time help

## Success Checklist

- [ ] Python 3.8+ installed
- [ ] Wikipedia MCP server installed (pipx or venv)
- [ ] Claude Desktop configuration updated
- [ ] Claude Desktop restarted
- [ ] Test query successful
- [ ] Ready to enhance your geographical database!

## Next Steps

1. **Read the examples**: Check out [EXAMPLES.md](EXAMPLES.md) for practical use cases
2. **Validate your data**: Use Wikipedia to cross-check key entries
3. **Enrich your database**: Add context and descriptions
4. **Share your workflows**: Contribute new use cases to the project

---

**Estimated time to complete**: 5 minutes  
**Difficulty level**: Beginner  
**Prerequisites**: Python 3.8+, Claude Desktop

Enjoy your Wikipedia-enhanced geographical database! 🌍📚
