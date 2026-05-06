#!/bin/bash
# Ubuntu Server Deployment Script
# Script untuk deploy Security Scanner ke Ubuntu Server

echo "=== Security Scanner System ==="
echo "Ubuntu Server Deployment Script"
echo "================================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "Berjalan sebagai root - OK"
else
   echo "Script ini membutuhkan akses sudo untuk instalasi optimal."
   echo "Beberapa fitur mungkin terbatas."
fi

# Update system
echo -e "\n[1/7] Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python and dependencies
echo -e "\n[2/7] Installing Python and system dependencies..."
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y build-essential python3-dev
sudo apt install -y curl wget git

# Install required system packages for psutil
sudo apt install -y gcc
sudo apt install -y python3-psutil || echo "Will install psutil via pip"

# Create project directory
echo -e "\n[3/7] Setting up project directory..."
PROJECT_DIR="/opt/security-scanner"
if [ ! -d "$PROJECT_DIR" ]; then
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown $USER:$USER "$PROJECT_DIR"
fi

# Copy project files (assuming current directory has the project)
echo -e "\n[4/7] Copying project files..."
cp -r * "$PROJECT_DIR/" 2>/dev/null || echo "Files copied with some warnings"

cd "$PROJECT_DIR"

# Create Python virtual environment
echo -e "\n[5/7] Creating Python virtual environment..."
python3 -m venv env --system-site-packages
source env/bin/activate

# Install Python dependencies
echo -e "\n[6/7] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment file
echo -e "\n[7/7] Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "Environment file created. Please edit .env with your credentials:"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - TELEGRAM_CHAT_ID" 
    echo "  - Install Ollama AI with: curl -fsSL https://ollama.ai/install.sh | sh"
fi

# Set permissions
echo -e "\nSetting permissions..."
sudo chown -R $USER:$USER "$PROJECT_DIR"
sudo chmod +x "$PROJECT_DIR"/*.py

# Create log directory
sudo mkdir -p /var/log/security-scanner
sudo chown $USER:$USER /var/log/security-scanner

echo -e "\n================================================="
echo "✅ INSTALASI SELESAI!"
echo "================================================="
echo
echo "📁 Project directory: $PROJECT_DIR"
echo "🐍 Virtual environment: $PROJECT_DIR/env"
echo "📝 Configuration file: $PROJECT_DIR/.env"
echo
echo "🔧 NEXT STEPS:"
echo "1. Install Ollama AI:"
echo "   curl -fsSL https://ollama.ai/install.sh | sh"
echo "   ollama serve &"
echo "   ollama pull llama3.2:1b"
echo
echo "2. Edit configuration file:"
echo "   cd $PROJECT_DIR && nano .env"
echo
echo "3. Test the system:"
echo "   cd $PROJECT_DIR && source env/bin/activate"
echo "   python -m core.host_utils"
echo
echo "4. Run full security scan (MAIN COMMAND):"
echo "   sudo $PROJECT_DIR/env/bin/python main_scanner.py"
echo
echo "5. (Optional) Review logs folder after scans:"
echo "   $PROJECT_DIR/logs/"
echo
echo "📊 TESTING:"
echo "- Host utilities test: python -m core.host_utils"
echo "- Full system scan: python main_scanner.py"
echo
echo "📜 LOGS akan tersimpan di:"
echo "- $PROJECT_DIR/logs/"
echo
echo "🚀 System ready! Just run: sudo python main_scanner.py"
