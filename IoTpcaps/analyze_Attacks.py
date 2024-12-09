import argparse
from scapy.all import rdpcap, IP, TCP
import os
from datetime import datetime, timedelta

# Mock list of known malicious IPs for demonstration
KNOWN_MALICIOUS_IPS = ["192.168.100.100", "192.168.100.101"]

def load_packets(file_path):
    """ Load packets from a pcap file. """
    try:
        return rdpcap(file_path)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

def convert_timestamps(packets):
    """ Convert packet timestamps to datetime objects along with the packet. """
    converted = []
    for pkt in packets:
        if IP in pkt and TCP in pkt:
            try:
                timestamp = float(pkt.time)
                converted.append((datetime.fromtimestamp(timestamp), pkt))
            except ValueError as e:
                print(f"Error converting timestamp: {e}")
    return converted

def filter_packets_by_time(packets, start_time, end_time):
    """ Filter packets within a specific time range. """
    return [pkt for ts, pkt in packets if start_time <= ts <= end_time]

def detect_protocol_violations(packets):
    """ Detect TCP flag violations or unusual protocol behavior. """
    for ts, pkt in packets:
        if TCP in pkt and (pkt[TCP].flags & 0x3F) == 0:  # Unusual TCP flag check
            print(f"Protocol violation detected: TCP packet with unusual flags at {ts}")

def detect_port_scanning(packets):
    """ Detect potential port scanning activities. """
    port_hits = {}
    for ts, pkt in packets:
        if TCP in pkt and pkt[TCP].dport not in port_hits:
            port_hits[pkt[TCP].dport] = 1
        else:
            port_hits[pkt[TCP].dport] += 1

    for port, count in port_hits.items():
        if count > 100:  # Threshold for suspecting port scanning
            print(f"Potential port scanning activity detected on port {port}")

def check_malicious_communications(packets):
    """ Check for communications with kn