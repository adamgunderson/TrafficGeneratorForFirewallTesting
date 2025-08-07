#!/usr/bin/env python3
# filename: traffic_generator.py

import random
import time
import argparse
import json
import logging
import sys
import signal
import os
from scapy.all import *
from datetime import datetime
import ipaddress

class TrafficGenerator:
    def __init__(self, config_file='traffic_config.json'):
        """Initialize the traffic generator with configuration"""
        self.running = True
        self.config = self.load_config(config_file)
        self.setup_logging()
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Config file {config_file} not found. Using defaults.")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration"""
        return {
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
            "tcp_ports": [22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 8443],
            "udp_ports": [53, 67, 68, 69, 123, 161, 162, 500, 514, 1194, 4500, 5060],
            "packet_interval": 0.1,
            "burst_mode": False,
            "burst_size": 10,
            "log_level": "INFO"
        }
    
    def setup_logging(self):
        """Configure logging"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/traffic_generator.log'),
                logging.StreamHandler()
            ]
        )
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logging.info(f"Received signal {signum}. Shutting down...")
        self.running = False
    
    def get_random_source_ip(self):
        """Generate random source IP from configured network"""
        network = ipaddress.IPv4Network(self.config['source_network'])
        # Exclude network and broadcast addresses
        hosts = list(network.hosts())
        # Also exclude our own IP (.2)
        hosts = [str(ip) for ip in hosts if str(ip) != '192.168.0.2']
        return random.choice(hosts) if hosts else '192.168.0.100'
    
    def get_random_target_ip(self):
        """Generate random target IP from configured networks"""
        target_network = random.choice(self.config['target_networks'])
        network = ipaddress.IPv4Network(target_network)
        hosts = list(network.hosts())
        return str(random.choice(hosts)) if hosts else '10.0.0.1'
    
    def generate_tcp_packet(self):
        """Generate random TCP packet"""
        src_ip = self.get_random_source_ip()
        dst_ip = self.get_random_target_ip()
        src_port = random.randint(1024, 65535)
        dst_port = random.choice(self.config['tcp_ports'])
        
        # Random TCP flags
        flags = random.choice(['S', 'SA', 'A', 'F', 'R', 'P'])
        
        packet = IP(src=src_ip, dst=dst_ip) / TCP(sport=src_port, dport=dst_port, flags=flags)
        
        # Add random payload sometimes
        if random.random() > 0.7:
            payload_size = random.randint(10, 1400)
            packet = packet / Raw(RandString(payload_size))
        
        return packet
    
    def generate_udp_packet(self):
        """Generate random UDP packet"""
        src_ip = self.get_random_source_ip()
        dst_ip = self.get_random_target_ip()
        src_port = random.randint(1024, 65535)
        dst_port = random.choice(self.config['udp_ports'])
        
        packet = IP(src=src_ip, dst=dst_ip) / UDP(sport=src_port, dport=dst_port)
        
        # Add random payload
        payload_size = random.randint(10, 1400)
        packet = packet / Raw(RandString(payload_size))
        
        return packet
    
    def generate_icmp_packet(self):
        """Generate random ICMP packet"""
        src_ip = self.get_random_source_ip()
        dst_ip = self.get_random_target_ip()
        
        # Random ICMP types
        icmp_types = [
            (8, 0),  # Echo Request
            (0, 0),  # Echo Reply
            (3, random.randint(0, 15)),  # Destination Unreachable
            (11, random.randint(0, 1)),  # Time Exceeded
            (4, 0),  # Source Quench
        ]
        
        icmp_type, icmp_code = random.choice(icmp_types)
        packet = IP(src=src_ip, dst=dst_ip) / ICMP(type=icmp_type, code=icmp_code)
        
        # Add payload for echo requests/replies
        if icmp_type in [0, 8]:
            packet = packet / Raw(RandString(random.randint(10, 64)))
        
        return packet
    
    def generate_traffic(self):
        """Main traffic generation loop"""
        logging.info("Starting traffic generation...")
        packet_count = 0
        
        while self.running:
            try:
                # Select random protocol
                protocol = random.choice(self.config['protocols'])
                
                if protocol == 'tcp':
                    packet = self.generate_tcp_packet()
                elif protocol == 'udp':
                    packet = self.generate_udp_packet()
                elif protocol == 'icmp':
                    packet = self.generate_icmp_packet()
                else:
                    continue
                
                # Send packet(s)
                if self.config.get('burst_mode', False):
                    # Send burst of packets
                    burst_size = self.config.get('burst_size', 10)
                    for _ in range(burst_size):
                        send(packet, verbose=0)
                        packet_count += 1
                else:
                    # Send single packet
                    send(packet, verbose=0)
                    packet_count += 1
                
                # Log periodically
                if packet_count % 100 == 0:
                    logging.info(f"Sent {packet_count} packets")
                
                # Sleep between packets/bursts
                time.sleep(self.config.get('packet_interval', 0.1))
                
            except PermissionError:
                logging.error("Permission denied. Please run as root (sudo).")
                self.running = False
            except Exception as e:
                logging.error(f"Error generating traffic: {e}")
                time.sleep(1)
        
        logging.info(f"Traffic generation stopped. Total packets sent: {packet_count}")
    
    def run_continuous(self):
        """Run in continuous mode (for service)"""
        logging.info("Running in continuous mode")
        self.generate_traffic()
    
    def run_duration(self, duration):
        """Run for specified duration in seconds"""
        logging.info(f"Running for {duration} seconds")
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < duration:
            self.generate_traffic()
    
    def run_count(self, count):
        """Send specified number of packets"""
        logging.info(f"Sending {count} packets")
        sent = 0
        
        while self.running and sent < count:
            protocol = random.choice(self.config['protocols'])
            
            if protocol == 'tcp':
                packet = self.generate_tcp_packet()
            elif protocol == 'udp':
                packet = self.generate_udp_packet()
            elif protocol == 'icmp':
                packet = self.generate_icmp_packet()
            else:
                continue
            
            send(packet, verbose=0)
            sent += 1
            
            if sent % 10 == 0:
                logging.info(f"Sent {sent}/{count} packets")
            
            time.sleep(self.config.get('packet_interval', 0.1))

def main():
    parser = argparse.ArgumentParser(description='Network Traffic Generator for Firewall Testing')
    parser.add_argument('-c', '--config', default='traffic_config.json', 
                        help='Configuration file path')
    parser.add_argument('-m', '--mode', choices=['continuous', 'duration', 'count'], 
                        default='continuous', help='Operation mode')
    parser.add_argument('-d', '--duration', type=int, default=60, 
                        help='Duration in seconds (for duration mode)')
    parser.add_argument('-n', '--count', type=int, default=100, 
                        help='Number of packets to send (for count mode)')
    parser.add_argument('--daemon', action='store_true', 
                        help='Run as daemon/service')
    
    args = parser.parse_args()
    
    # Check if running as root
    if os.geteuid() != 0:
        print("This script must be run as root (sudo) to send raw packets.")
        sys.exit(1)
    
    # Create traffic generator instance
    generator = TrafficGenerator(args.config)
    
    # Run based on mode
    if args.mode == 'continuous' or args.daemon:
        generator.run_continuous()
    elif args.mode == 'duration':
        generator.run_duration(args.duration)
    elif args.mode == 'count':
        generator.run_count(args.count)

if __name__ == '__main__':
    main()