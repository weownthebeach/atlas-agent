#!/bin/bash
# ATLAS Web Tester - One-Click Installer for Mac

echo "🔍 ATLAS Web Tester Installer"
echo "=============================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Installing via Homebrew..."
    if ! command -v brew &> /dev/null; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python
fi

echo "✅ Python found: $(python3 --version)"

# Install ATLAS
echo ""
echo "📦 Installing ATLAS..."
pip3 install --upgrade pip
pip3 install git+https://github.com/weownthebeach/atlas-agent.git

# Install Playwright
echo ""
echo "🌐 Installing browser..."
python3 -m playwright install chromium

# Get API key
echo ""
echo "=============================="
echo "🔑 Enter your Anthropic API Key"
echo "   (Get one at: https://console.anthropic.com/)"
echo ""
read -p "API Key: " api_key

# Create .env file
echo "ANTHROPIC_API_KEY=$api_key" > ~/.atlas-env

echo ""
echo "✅ Installation complete!"
echo ""
echo "=============================="
echo "🚀 Starting ATLAS Web Interface..."
echo "   Open http://localhost:8000 in your browser"
echo "=============================="
echo ""

# Start the server
export ANTHROPIC_API_KEY=$api_key
atlas web
