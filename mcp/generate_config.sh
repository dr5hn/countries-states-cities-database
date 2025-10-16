#!/bin/bash

# Generate Claude Desktop configuration for Wikipedia MCP Server

set -e  # Exit on error

echo "=========================================="
echo "Claude Desktop Configuration Generator"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Detect installation method
print_info "Detecting Wikipedia MCP server installation..."

# Check for pipx installation
if command -v pipx &> /dev/null; then
    if pipx list | grep -q "wikipedia-mcp"; then
        INSTALL_METHOD="pipx"
        COMMAND="wikipedia-mcp"
        print_success "Found pipx installation"
    fi
fi

# Check for virtual environment installation
if [ -z "$INSTALL_METHOD" ] && [ -f "$SCRIPT_DIR/venv/bin/wikipedia-mcp" ]; then
    INSTALL_METHOD="venv"
    COMMAND="$SCRIPT_DIR/venv/bin/wikipedia-mcp"
    print_success "Found virtual environment installation"
fi

# If not found, ask user
if [ -z "$INSTALL_METHOD" ]; then
    print_warning "Could not detect Wikipedia MCP server installation"
    echo ""
    echo "How did you install the Wikipedia MCP server?"
    echo "1) pipx (use command: wikipedia-mcp)"
    echo "2) Virtual environment in mcp/venv"
    echo "3) Custom installation (specify path)"
    echo ""
    read -p "Enter your choice (1, 2, or 3): " choice
    
    case $choice in
        1)
            INSTALL_METHOD="pipx"
            COMMAND="wikipedia-mcp"
            ;;
        2)
            INSTALL_METHOD="venv"
            COMMAND="$SCRIPT_DIR/venv/bin/wikipedia-mcp"
            ;;
        3)
            read -p "Enter the full path to wikipedia-mcp: " CUSTOM_PATH
            INSTALL_METHOD="custom"
            COMMAND="$CUSTOM_PATH"
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
fi

# Detect operating system
print_info "Detecting operating system..."
OS=""
CONFIG_PATH=""

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    CONFIG_PATH="$HOME/.config/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="Windows"
    CONFIG_PATH="$APPDATA/Claude/claude_desktop_config.json"
else
    OS="Unknown"
    CONFIG_PATH="$HOME/.config/Claude/claude_desktop_config.json"
fi

print_success "Detected OS: $OS"

# Generate configuration
print_info "Generating configuration file..."

CONFIG_FILE="$SCRIPT_DIR/claude_desktop_config.json"

cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "wikipedia": {
      "command": "$COMMAND"
    }
  }
}
EOF

print_success "Configuration file generated: $CONFIG_FILE"

# Display the configuration
echo ""
echo "=========================================="
echo "Generated Configuration:"
echo "=========================================="
cat "$CONFIG_FILE"
echo "=========================================="
echo ""

# Provide instructions
print_info "Next steps:"
echo ""
echo "1. Copy the configuration to Claude Desktop's config location:"
echo ""

if [ "$OS" == "macOS" ]; then
    echo "   mkdir -p \"$HOME/Library/Application Support/Claude\""
    echo "   cp \"$CONFIG_FILE\" \"$CONFIG_PATH\""
elif [ "$OS" == "Linux" ]; then
    echo "   mkdir -p \"$HOME/.config/Claude\""
    echo "   cp \"$CONFIG_FILE\" \"$CONFIG_PATH\""
elif [ "$OS" == "Windows" ]; then
    echo "   mkdir -p \"%APPDATA%\\Claude\""
    echo "   copy \"$CONFIG_FILE\" \"%APPDATA%\\Claude\\claude_desktop_config.json\""
else
    echo "   mkdir -p \"$HOME/.config/Claude\""
    echo "   cp \"$CONFIG_FILE\" \"$CONFIG_PATH\""
fi

echo ""
echo "   Or manually copy the content above to: $CONFIG_PATH"
echo ""
echo "2. If Claude Desktop config already exists, merge this configuration:"
echo "   - Open $CONFIG_PATH"
echo "   - Add the 'wikipedia' entry under 'mcpServers'"
echo ""
echo "3. Restart Claude Desktop"
echo ""
echo "4. Test the integration with a prompt like:"
echo "   'Tell me about Tokyo using Wikipedia information'"
echo ""

# Offer to copy automatically
if [ -f "$CONFIG_PATH" ]; then
    print_warning "Claude Desktop config already exists at: $CONFIG_PATH"
    echo ""
    read -p "Do you want to backup and replace it? (y/N): " replace
    
    if [[ $replace =~ ^[Yy]$ ]]; then
        BACKUP_FILE="${CONFIG_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
        print_info "Creating backup: $BACKUP_FILE"
        cp "$CONFIG_PATH" "$BACKUP_FILE"
        
        print_info "Replacing configuration..."
        cp "$CONFIG_FILE" "$CONFIG_PATH"
        
        print_success "Configuration updated! Backup saved to: $BACKUP_FILE"
        print_warning "Please restart Claude Desktop for changes to take effect"
    else
        print_info "Please manually merge the configuration"
    fi
else
    echo ""
    read -p "Do you want to copy the config to Claude Desktop now? (Y/n): " copy_now
    
    if [[ ! $copy_now =~ ^[Nn]$ ]]; then
        # Create directory if it doesn't exist
        CONFIG_DIR=$(dirname "$CONFIG_PATH")
        mkdir -p "$CONFIG_DIR"
        
        print_info "Copying configuration to: $CONFIG_PATH"
        cp "$CONFIG_FILE" "$CONFIG_PATH"
        
        print_success "Configuration copied successfully!"
        print_warning "Please restart Claude Desktop for changes to take effect"
    fi
fi

echo ""
print_success "Configuration generation complete!"
print_info "See mcp/README.md for usage examples"
