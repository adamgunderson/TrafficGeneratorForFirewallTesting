#!/bin/bash
# filename: setup.sh

set -e

echo "==================================="
echo "Traffic Generator Setup Script"
echo "==================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (sudo ./setup.sh)" 
   exit 1
fi

# Update package list
echo "Updating package list..."
apt-get update

# Install required packages
echo "Installing required packages..."
apt-get install -y python3 python3-pip python3-venv tcpdump iptables

# Install Python packages
echo "Installing Python packages..."
pip3 install scapy

# Create directory structure
echo "Creating directory structure..."
mkdir -p /opt/traffic-generator
mkdir -p /var/log

# Copy files
echo "Copying files..."
cp traffic_generator.py /opt/traffic-generator/
cp traffic_config.json /opt/traffic-generator/
cp traffic-generator.service /etc/systemd/system/

# Set permissions
echo "Setting permissions..."
chmod +x /opt/traffic-generator/traffic_generator.py
chmod 644 /opt/traffic-generator/traffic_config.json
chmod 644 /etc/systemd/system/traffic-generator.service

# Create log file
touch /var/log/traffic_generator.log
chmod 666 /var/log/traffic_generator.log

# Reload systemd
echo "Reloading systemd..."
systemctl daemon-reload

echo ""
echo "==================================="
echo "Installation Complete!"
echo "==================================="
echo ""
echo "Usage:"
echo "------"
echo ""
echo "1. Ad-hoc mode (run for 60 seconds):"
echo "   sudo python3 /opt/traffic-generator/traffic_generator.py -m duration -d 60"
echo ""
echo "2. Ad-hoc mode (send 1000 packets):"
echo "   sudo python3 /opt/traffic-generator/traffic_generator.py -m count -n 1000"
echo ""
echo "3. Start as service:"
echo "   sudo systemctl start traffic-generator"
echo ""
echo "4. Enable service at boot:"
echo "   sudo systemctl enable traffic-generator"
echo ""
echo "5. Check service status:"
echo "   sudo systemctl status traffic-generator"
echo ""
echo "6. View logs:"
echo "   sudo journalctl -u traffic-generator -f"
echo "   or"
echo "   sudo tail -f /var/log/traffic_generator.log"
echo ""
echo "Configuration file: /opt/traffic-generator/traffic_config.json"