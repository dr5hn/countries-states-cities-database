#!/bin/bash

# Wikipedia MCP Server Installation Script
# This script installs the Wikipedia MCP server for the Countries States Cities Database project

set -e  # Exit on error

echo "=========================================="
echo "Wikipedia MCP Server Installation"
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

# Check if Python 3 is installed
print_info "Checking for Python 3..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# Prompt user for installation method
echo ""
echo "Choose installation method:"
echo "1) pipx (Recommended - isolated installation)"
echo "2) Virtual environment (Local to this project)"
echo ""
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        print_info "Installing using pipx..."
        
        # Check if pipx is installed
        if ! command -v pipx &> /dev/null; then
            print_warning "pipx is not installed. Attempting to install pipx..."
            
            # Try to install pipx
            if command -v apt &> /dev/null; then
                sudo apt update && sudo apt install -y pipx
            elif command -v brew &> /dev/null; then
                brew install pipx
            else
                print_error "Could not install pipx automatically. Please install it manually:"
                print_error "  Ubuntu/Debian: sudo apt install pipx"
                print_error "  macOS: brew install pipx"
                print_error "  Other: python3 -m pip install --user pipx"
                exit 1
            fi
            
            # Ensure pipx path is configured
            pipx ensurepath
            print_success "pipx installed"
        fi
        
        # Install Wikipedia MCP server
        print_info "Installing Wikipedia MCP server..."
        pipx install git+https://github.com/rudra-ravi/wikipedia-mcp.git
        
        print_success "Wikipedia MCP server installed successfully via pipx"
        echo ""
        print_info "You can now run the server with: wikipedia-mcp"
        print_info "Don't forget to add it to your shell configuration:"
        echo "    pipx ensurepath"
        echo "    source ~/.bashrc  # or ~/.zshrc for zsh"
        ;;
        
    2)
        print_info "Installing using virtual environment..."
        
        # Get the directory of this script
        SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
        
        # Create virtual environment
        print_info "Creating virtual environment in $SCRIPT_DIR/venv..."
        python3 -m venv "$SCRIPT_DIR/venv"
        
        # Activate virtual environment
        print_info "Activating virtual environment..."
        source "$SCRIPT_DIR/venv/bin/activate"
        
        # Upgrade pip
        print_info "Upgrading pip..."
        pip install --upgrade pip
        
        # Install Wikipedia MCP server
        print_info "Installing Wikipedia MCP server..."
        pip install git+https://github.com/rudra-ravi/wikipedia-mcp.git
        
        print_success "Wikipedia MCP server installed successfully in virtual environment"
        echo ""
        print_info "To use the server, activate the virtual environment first:"
        echo "    cd $SCRIPT_DIR"
        echo "    source venv/bin/activate"
        echo "    wikipedia-mcp"
        echo ""
        print_info "To deactivate the virtual environment:"
        echo "    deactivate"
        ;;
        
    *)
        print_error "Invalid choice. Please run the script again and choose 1 or 2."
        exit 1
        ;;
esac

echo ""
echo "=========================================="
print_success "Installation complete!"
echo "=========================================="
echo ""
print_info "Next steps:"
echo "1. Configure Claude Desktop (run: bash mcp/generate_config.sh)"
echo "2. Copy the generated config to Claude Desktop's config location"
echo "3. Restart Claude Desktop"
echo "4. Start using Wikipedia queries in Claude!"
echo ""
print_info "See mcp/README.md for detailed usage instructions"
