# Traffic Generator for Firewall Testing

A comprehensive network traffic generator for testing firewall rules on Debian servers. This tool generates randomized network traffic with spoofed source addresses to simulate various network conditions.

## Features

- **Multi-Protocol Support**: TCP, UDP, and ICMP traffic generation
- **IP Spoofing**: Randomize source IPs within configured network ranges
- **Multiple Target Networks**: Test against multiple destination networks simultaneously
- **Flexible Operation Modes**:
  - Ad-hoc mode for quick testing
  - Service mode for continuous operation
  - Duration-based testing
  - Packet count-based testing
- **Configurable Parameters**: JSON-based configuration for easy customization
- **Comprehensive Logging**: Detailed logs for analysis and debugging
- **Control Panel**: Interactive menu-driven control script

## Network Configuration

- **Server IP**: 192.168.0.2
- **Source Network**: 192.168.0.0/24 (spoofed addresses)
- **Target Networks**:
  - 192.168.100.0/24
  - 10.0.0.0/24
  - 192.168.0.0/24
  - 192.168.1.0/24
  - 192.168.3.0/24
  - 192.168.4.0/24
  - 192.168.5.0/24

## Installation

1. **Clone or download all files** to your Debian server

2. **Run the setup script**:
```bash
sudo chmod +x setup.sh
sudo ./setup.sh
```

This will:
- Install required packages (Python3, Scapy, tcpdump)
- Create directory structure in `/opt/traffic-generator/`
- Install systemd service
- Set up logging

## Usage

### Method 1: Interactive Control Panel (Recommended)

```bash
sudo chmod +x traffic-control.sh
sudo ./traffic-control.sh
```

This provides a menu-driven interface with options for:
- Quick tests
- Timed tests
- Service management
- Configuration editing
- Network statistics
- Stress testing

### Method 2: Direct Command Line

#### Ad-hoc Testing

**Quick test (100 packets)**:
```bash
sudo python3 /opt/traffic-generator/traffic_generator.py -m count -n 100
```

**Timed test (60 seconds)**:
```bash
sudo python3 /opt/traffic-generator/traffic_generator.py -m duration -d 60
```

**Custom packet count**:
```bash
sudo python3 /opt/traffic-generator/traffic_generator.py -m count -n 5000
```

#### Service Mode

**Start the service**:
```bash
sudo systemctl start traffic-generator
```

**Stop the service**:
```bash
sudo systemctl stop traffic-generator
```

**Enable at boot**:
```bash
sudo systemctl enable traffic-generator
```

**Check status**:
```bash
sudo systemctl status traffic-generator
```

**View logs**:
```bash
# Service logs
sudo journalctl -u traffic-generator -f

# Application logs
sudo tail -f /var/log/traffic_generator.log
```

## Configuration

Edit `/opt/traffic-generator/traffic_config.json` to customize:

```json
{
  "source_network": "192.168.0.0/24",
  "target_networks": [...],
  "protocols": ["tcp", "udp", "icmp"],
  "tcp_ports": [22, 80, 443, ...],
  "udp_ports": [53, 123, ...],
  "packet_interval": 0.1,
  "burst_mode": false,
  "burst_size": 10,
  "log_level": "INFO"
}
```

### Configuration Parameters

- **source_network**: Network range for spoofed source IPs
- **target_networks**: List of destination networks
- **protocols**: Enabled protocols (tcp/udp/icmp)
- **tcp_ports**: TCP destination ports
- **udp_ports**: UDP destination ports
- **packet_interval**: Delay between packets (seconds)
- **burst_mode**: Enable burst transmission
- **burst_size**: Packets per burst
- **log_level**: Logging verbosity (DEBUG/INFO/WARNING/ERROR)

## Traffic Patterns

The generator creates realistic traffic patterns including:

### TCP Traffic
- SYN, SYN-ACK, ACK, FIN, RST packets
- Random source ports (1024-65535)
- Configurable destination ports
- Optional payload data

### UDP Traffic
- Random source/destination ports
- Variable payload sizes (10-1400 bytes)
- Common service ports (DNS, NTP, SNMP, etc.)

### ICMP Traffic
- Echo requests/replies
- Destination unreachable
- Time exceeded
- Source quench
- Variable payload sizes

## Testing Scenarios

### Basic Firewall Test
```bash
# Generate mixed traffic for 5 minutes
sudo python3 /opt/traffic-generator/traffic_generator.py -m duration -d 300
```

### Port-Specific Testing
Edit config to test specific ports:
```json
{
  "tcp_ports": [22, 80, 443],
  "protocols": ["tcp"]
}
```

### Stress Testing
Use the control panel's stress test option or:
```bash
# Create stress config with minimal interval
# packet_interval: 0.001, burst_mode: true, burst_size: 50
sudo ./traffic-control.sh
# Select option 10 for stress test
```

## Monitoring

### Watch traffic in real-time:
```bash
sudo tcpdump -nn -i any 'net 192.168.0.0/24 or net 192.168.100.0/24'
```

### Check iptables counters:
```bash
sudo iptables -L -n -v
```

### Monitor interface statistics:
```bash
watch -n 1 'ip -s link show'
```

## Security Considerations

- **Root Access Required**: Raw packet generation requires root privileges
- **Internal Use Only**: Designed for testing on private networks
- **Resource Limits**: Service configured with CPU and memory limits
- **Logging**: All activities are logged for audit purposes

## Troubleshooting

### Permission Denied
Ensure running as root:
```bash
sudo python3 /opt/traffic-generator/traffic_generator.py
```

### Service Won't Start
Check logs:
```bash
sudo journalctl -u traffic-generator -n 50
```

### High CPU Usage
Adjust packet_interval in config:
```json
"packet_interval": 0.5
```

### No Traffic Generated
Verify network configuration:
```bash
ip addr show
ip route show
```

## Uninstallation

```bash
# Stop and disable service
sudo systemctl stop traffic-generator
sudo systemctl disable traffic-generator

# Remove files
sudo rm -rf /opt/traffic-generator
sudo rm /etc/systemd/system/traffic-generator.service
sudo rm /var/log/traffic_generator.log

# Reload systemd
sudo systemctl daemon-reload
```

## License

This tool is for network testing and educational purposes only. Use responsibly and only on networks you own or have permission to test.

## Support

For issues or questions, check:
1. Application logs: `/var/log/traffic_generator.log`
2. Service logs: `journalctl -u traffic-generator`
3. Network configuration: `ip addr` and `ip route`