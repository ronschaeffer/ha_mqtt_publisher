#!/bin/bash
# Run the MQTT Publisher

# Set locale to avoid git warnings
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Running 📡 MQTT Publisher...${NC}"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the module
echo -e "${BLUE}📡 Starting MQTT Publisher...${NC}"
python -m mqtt_publisher

echo -e "${GREEN}✅ MQTT Publisher finished${NC}"
