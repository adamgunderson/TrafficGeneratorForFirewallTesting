# Quick Start Guide - Traffic Generator

## 🚀 5-Minute Setup

### Step 1: Download Files
Place these files in a directory on your Debian server:
- `traffic_generator.py` - Main script
- `traffic_config.json` - Configuration
- `traffic-generator.service` - Service file
- `setup.sh` - Installation script
- `traffic-control.sh` - Control panel

### Step 2: Install
```bash
sudo chmod +x setup.sh
sudo ./setup.sh
```

### Step 3: Test It!
```bash
# Quick 100-packet test
sudo python3 /opt/traffic-generator/traffic_generator.py -m count -n 100
```

## 🎮 Easy Control Panel

For the easiest experience, use the control panel:
```bash
sudo chmod +x traffic-control.sh
sudo ./traffic-control.sh
```

Then just pick an option from the menu!

## 🔧 Common Commands

### Ad-hoc Testing
```bash
# Send 500 packets
sudo python3 /opt/traffic-generator/traffic_generator.py -m count -n 500

# Run for 30 seconds
sudo python3 /opt/traffic-generator/traffic_generator.py -m duration -d 30
```

### Run as Service
```bash
# Start
sudo systemctl start traffic-generator

# Stop
sudo systemctl stop traffic-generator

# Check status
sudo systemctl status traffic-generator
```

## 📊 Monitor Traffic

Watch the traffic being generated:
```bash
sudo tcpdump -nn -c 20
```

Check the logs:
```bash
sudo tail -f /var/log/traffic_generator.log
```

## ⚙️ Quick Config Changes

Edit `/opt/traffic-generator/traffic_config.json`:

**Faster traffic** (be careful!):
```json
"packet_interval": 0.01
```

**TCP only**:
```json
"protocols": ["tcp"]
```

**Specific ports only**:
```json
"tcp_ports": [80, 443]
```

## ⚠️ Important Notes

1. **Must run as root** (sudo)
2. **Private networks only** - Don't use on public networks
3. **Default is safe** - 0.1 second between packets
4. **Logs everything** - Check `/var/log/traffic_generator.log`

## 🆘 Troubleshooting

**"Permission denied"**
→ Use `sudo`

**"Service won't start"**
→ Check: `sudo journalctl -u traffic-generator -n 20`

**"Too much traffic!"**
→ Increase packet_interval in config (e.g., 0.5 or 1.0)

**"No traffic visible"**
→ Check with: `sudo tcpdump -nn -i any`

---
That's it! You're ready to test your firewall rules. 🎯