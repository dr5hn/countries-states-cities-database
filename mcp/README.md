# Wikipedia MCP Server Integration

This directory contains configuration and scripts for integrating the Wikipedia MCP (Model Context Protocol) Server with the Countries States Cities Database project.

## What is MCP?

The Model Context Protocol (MCP) is a standardized protocol that allows AI assistants (like Claude) to interact with external data sources and tools. By integrating the Wikipedia MCP server, we can enhance our geographical database with rich contextual information from Wikipedia.

## Features

With the Wikipedia MCP server integrated, you can:

- 🔍 **Search Wikipedia articles** related to countries, states, and cities
- 📖 **Retrieve article summaries** for geographical entities
- 📄 **Get full article content** for detailed information
- 🗂️ **Extract specific sections** from Wikipedia articles
- 🔗 **Find related links** within articles

## Use Cases for This Project

1. **Data Enrichment**: Get additional context about countries, states, and cities
2. **Validation**: Cross-reference geographical data with Wikipedia entries
3. **Historical Context**: Access historical information about locations
4. **Cultural Information**: Retrieve cultural and demographic details
5. **Documentation**: Generate rich documentation with Wikipedia references

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or pipx package manager

### Installation Methods

#### Option 1: Using pipx (Recommended)

```bash
# Install pipx if you don't have it
sudo apt install pipx
pipx ensurepath

# Install the Wikipedia MCP server
pipx install git+https://github.com/rudra-ravi/wikipedia-mcp.git
```

#### Option 2: Using Virtual Environment

```bash
# Navigate to the MCP directory
cd mcp

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the package
pip install git+https://github.com/rudra-ravi/wikipedia-mcp.git
```

#### Option 3: Using the Installation Script

We provide a convenient installation script:

```bash
# From the project root
bash mcp/install.sh
```

## Configuration

### For Claude Desktop

Add the following configuration to your Claude Desktop configuration file:

**Configuration file location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Configuration content:**

```json
{
  "mcpServers": {
    "wikipedia": {
      "command": "wikipedia-mcp"
    }
  }
}
```

If you installed using a virtual environment, use this configuration instead:

```json
{
  "mcpServers": {
    "wikipedia": {
      "command": "/path/to/countries-states-cities-database/mcp/venv/bin/wikipedia-mcp"
    }
  }
}
```

You can use the provided configuration generator:

```bash
# From the project root
bash mcp/generate_config.sh
```

This will create a `claude_desktop_config.json` file in the `mcp/` directory that you can copy to your Claude Desktop configuration location.

## Usage

### Running the Server

#### If installed with pipx:

```bash
wikipedia-mcp
```

#### If installed in a virtual environment:

```bash
cd mcp
source venv/bin/activate
wikipedia-mcp
```

### Example Prompts

Once the server is running and configured with Claude Desktop, you can use prompts like:

#### For This Project Context:

- "Using Wikipedia, tell me about the history and geography of Tokyo, Japan"
- "Get Wikipedia information about New York City and its boroughs"
- "Summarize the Wikipedia article for Paris, France focusing on demographics"
- "What does Wikipedia say about the administrative divisions of Germany?"
- "Find Wikipedia information about the capital cities of all Nordic countries"

#### General Queries:

- "Tell me about quantum computing using Wikipedia information"
- "Summarize the history of artificial intelligence based on Wikipedia"
- "What does Wikipedia say about climate change?"

## Integration with Project Workflows

### Data Validation Workflow

```bash
# 1. Query a city in the database
mysql -uroot -proot -e "SELECT * FROM world.cities WHERE name='Tokyo' LIMIT 1;"

# 2. Use Claude with Wikipedia MCP to verify the information
# Claude can now: "Check Wikipedia for Tokyo's current population and timezone"

# 3. Update data if needed
vim contributions/cities/JP.json
```

### Data Enrichment Workflow

```bash
# 1. Identify cities needing additional context
mysql -uroot -proot -e "SELECT name, country_code FROM world.cities WHERE country_code='FR' LIMIT 10;"

# 2. Use Claude with Wikipedia MCP
# Claude can: "For each of these French cities, get a brief description from Wikipedia"

# 3. Store the enriched information (if implementing new fields)
```

## Architecture

```
┌─────────────────────────────────────────┐
│   Claude Desktop / AI Assistant         │
│   (with MCP support)                    │
└────────────────┬────────────────────────┘
                 │
                 │ MCP Protocol
                 │
┌────────────────▼────────────────────────┐
│   Wikipedia MCP Server                  │
│   (wikipedia-mcp)                       │
└────────────────┬────────────────────────┘
                 │
                 │ Wikipedia API
                 │
┌────────────────▼────────────────────────┐
│   Wikipedia                             │
│   (External Data Source)                │
└─────────────────────────────────────────┘
```

## Files in This Directory

- `README.md` - This documentation file
- `install.sh` - Installation script for the Wikipedia MCP server
- `generate_config.sh` - Script to generate Claude Desktop configuration
- `claude_desktop_config.json` - Sample configuration file (generated)
- `venv/` - Virtual environment (if using local installation)

## Troubleshooting

### Server Not Starting

```bash
# Check if the package is installed
pipx list | grep wikipedia-mcp
# or
pip list | grep wikipedia

# Reinstall if needed
pipx uninstall wikipedia-mcp
pipx install git+https://github.com/rudra-ravi/wikipedia-mcp.git
```

### Claude Desktop Not Recognizing the Server

1. Ensure the configuration file is in the correct location
2. Restart Claude Desktop after adding the configuration
3. Check the command path in the configuration matches your installation

### Permission Issues

```bash
# If using pipx
pipx ensurepath
source ~/.bashrc  # or ~/.zshrc

# If using virtual environment, ensure it's activated
source mcp/venv/bin/activate
```

## Contributing

Improvements to the MCP integration are welcome! Please ensure:

1. All scripts are tested on Linux, macOS, and Windows (where applicable)
2. Documentation is updated with any new features
3. Configuration examples are provided for different installation methods

## Credits

- **Wikipedia MCP Server**: Built by [Ravikumar E](https://github.com/rudra-ravi)
- **MCP Protocol**: Developed by Anthropic
- **Repository**: https://github.com/rudra-ravi/wikipedia-mcp

## License

The Wikipedia MCP server is licensed under the MIT License. See the [original repository](https://github.com/rudra-ravi/wikipedia-mcp) for details.

This integration documentation is part of the Countries States Cities Database project, licensed under ODbL-1.0.
