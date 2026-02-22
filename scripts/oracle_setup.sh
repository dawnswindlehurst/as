#!/bin/bash
set -e

echo "=========================================="
echo "Capivara Bet - Oracle Cloud Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please do not run this script as root${NC}"
    exit 1
fi

echo -e "${GREEN}[1/8] Checking system requirements...${NC}"
# Check OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "OS: $NAME $VERSION"
else
    echo -e "${RED}Cannot determine OS${NC}"
    exit 1
fi

# Check RAM
total_ram=$(free -g | awk '/^Mem:/{print $2}')
echo "Total RAM: ${total_ram}GB"
if [ "$total_ram" -lt 10 ]; then
    echo -e "${YELLOW}Warning: Less than 12GB RAM detected. This may cause performance issues.${NC}"
fi

echo -e "${GREEN}[2/8] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing..."
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    echo "Docker installed successfully"
else
    echo "Docker already installed: $(docker --version)"
fi

echo -e "${GREEN}[3/8] Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found. Installing..."
    
    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo "Docker Compose installed successfully"
else
    echo "Docker Compose already installed: $(docker-compose --version)"
fi

echo -e "${GREEN}[4/8] Configuring firewall...${NC}"
# Configure firewall for Oracle Cloud
if command -v iptables &> /dev/null; then
    echo "Configuring iptables..."
    
    # Allow HTTP/HTTPS
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
    
    # Allow API port
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
    
    # Allow Dashboard port
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8501 -j ACCEPT
    
    # Save iptables rules
    if command -v netfilter-persistent &> /dev/null; then
        sudo netfilter-persistent save
    elif [ -f /etc/redhat-release ]; then
        sudo service iptables save
    fi
    
    echo "Firewall configured"
else
    echo -e "${YELLOW}iptables not found, skipping firewall configuration${NC}"
fi

echo -e "${GREEN}[5/8] Creating application directories...${NC}"
# Create necessary directories
mkdir -p ~/capivara-bet/data
mkdir -p ~/capivara-bet/logs
mkdir -p ~/capivara-bet/postgres_data

echo "Directories created"

echo -e "${GREEN}[6/8] Setting up swap (optional, for safety)...${NC}"
# Create swap file if not exists and total RAM < 12GB
if [ "$total_ram" -lt 12 ] && [ ! -f /swapfile ]; then
    echo "Creating 4GB swap file..."
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    
    # Make swap permanent
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    
    echo "Swap file created and activated"
else
    echo "Swap already configured or not needed"
fi

echo -e "${GREEN}[7/8] Installing system dependencies...${NC}"
# Install required packages
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y curl git vim htop net-tools
elif command -v yum &> /dev/null; then
    sudo yum install -y curl git vim htop net-tools
fi

echo -e "${GREEN}[8/8] Setting up environment...${NC}"
# Clone repository if not exists
if [ ! -d ~/capivara-bet/.git ]; then
    echo "Please clone the repository manually to ~/capivara-bet"
    echo "git clone <repository-url> ~/capivara-bet"
else
    echo "Repository already cloned"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Configure your .env file with required credentials"
echo "2. Run ./scripts/deploy.sh to start the application"
echo ""
echo -e "${YELLOW}Note: You may need to log out and back in for Docker group changes to take effect${NC}"
