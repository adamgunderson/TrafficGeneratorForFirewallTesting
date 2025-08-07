#!/bin/bash
# filename: traffic-control.sh

SCRIPT_PATH="/opt/traffic-generator/traffic_generator.py"
CONFIG_PATH="/opt/traffic-generator/traffic_config.json"
SERVICE_NAME="traffic-generator"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}This script must be run as root (sudo)${NC}"
        exit 1
    fi
}

# Display menu
show_menu() {
    echo -e "\n${GREEN}=== Traffic Generator Control Panel ===${NC}"
    echo "1. Quick test (100 packets)"
    echo "2. Timed test (custom duration)"
    echo "3. Packet count test (custom count)"
    echo "4. Start service (continuous)"
    echo "5. Stop service"
    echo "6. Service status"
    echo "7. View live logs"
    echo "8. Edit configuration"
    echo "9. Network statistics"
    echo "10. Stress test mode"
    echo "0. Exit"
    echo -n "Choose option: "
}

# Quick test
quick_test() {
    echo -e "${YELLOW}Running quick test (100 packets)...${NC}"
    python3 $SCRIPT_PATH -m count -n 100
}

# Timed test
timed_test() {
    read -p "Enter duration in seconds: " duration
    echo -e "${YELLOW}Running test for $duration seconds...${NC}"
    python3 $SCRIPT_PATH -m duration -d $duration
}

# Packet count test
packet_test() {
    read -p "Enter number of packets: " count
    echo -e "${YELLOW}Sending $count packets...${NC}"
    python3 $SCRIPT_PATH -m count -n $count
}

# Start service
start_service() {
    echo -e "${YELLOW}Starting traffic generator service...${NC}"
    systemctl start $SERVICE_NAME
    sleep 2
    systemctl status $SERVICE_NAME --no-pager
}

# Stop service
stop_service() {
    echo -e "${YELLOW}Stopping traffic generator service...${NC}"
    systemctl stop $SERVICE_NAME
    echo -e "${GREEN}Service stopped${NC}"
}

# Service status
service_status() {
    systemctl status $SERVICE_NAME --no-pager
}

# View logs
view_logs() {
    echo -e "${YELLOW}Showing live logs (press Ctrl+C to exit)...${NC}"
    tail -f /var/log/traffic_generator.log
}

# Edit configuration
edit_config() {
    if command -v nano &> /dev/null; then
        nano $CONFIG_PATH
    elif command -v vi &> /dev/null; then
        vi $CONFIG_PATH
    else
        echo -e "${RED}No text editor found${NC}"
    fi
}

# Network statistics
network_stats() {
    echo -e "${GREEN}=== Network Statistics ===${NC}"
    echo -e "\n${YELLOW}Interface Statistics:${NC}"
    ip -s link show
    
    echo -e "\n${YELLOW}Recent Traffic (last 10 packets):${NC}"
    timeout 5 tcpdump -c 10 -nn 2>/dev/null || echo "No traffic captured"
    
    echo -e "\n${YELLOW}Firewall Rules:${NC}"
    iptables -L -n -v | head -20
}

# Stress test mode
stress_test() {
    echo -e "${RED}WARNING: Stress test will generate high traffic volume!${NC}"
    read -p "Are you sure? (y/n): " confirm
    
    if [[ $confirm == "y" || $confirm == "Y" ]]; then
        echo -e "${YELLOW}Creating temporary stress config...${NC}"
        
        # Create temporary config for stress testing
        cat > /tmp/stress_config.json <<EOF
{
  "source_network": "192.168.0.0/24",
  "target_networks": [
    "192.168.100.0/24",
    "10.0.0.0/24",
    "192.168.0.0/24",
    "192.168.1.0/24",
    "192.168.3.0/24",
    "192.168.4.0/24",
    "192.168.5.0/24"
  ],
  "protocols": ["tcp", "udp", "icmp"],
  "tcp_ports": [22, 80, 443, 3306, 8080],
  "udp_ports": [53, 123, 161, 514],
  "packet_interval": 0.001,
  "burst_mode": true,
  "burst_size": 50,
  "log_level": "WARNING"
}
EOF
        
        read -p "Enter stress test duration (seconds): " stress_duration
        echo -e "${RED}Starting stress test for $stress_duration seconds...${NC}"
        python3 $SCRIPT_PATH -c /tmp/stress_config.json -m duration -d $stress_duration
        
        rm -f /tmp/stress_config.json
        echo -e "${GREEN}Stress test completed${NC}"
    else
        echo "Stress test cancelled"
    fi
}

# Main loop
main() {
    check_root
    
    while true; do
        show_menu
        read choice
        
        case $choice in
            1) quick_test ;;
            2) timed_test ;;
            3) packet_test ;;
            4) start_service ;;
            5) stop_service ;;
            6) service_status ;;
            7) view_logs ;;
            8) edit_config ;;
            9) network_stats ;;
            10) stress_test ;;
            0) echo -e "${GREEN}Exiting...${NC}"; exit 0 ;;
            *) echo -e "${RED}Invalid option${NC}" ;;
        esac
        
        echo -e "\nPress Enter to continue..."
        read
    done
}

# Run main function
main