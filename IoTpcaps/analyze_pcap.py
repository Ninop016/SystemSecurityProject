import argparse
from scapy.all import rdpcap, TCP
import os
import re
import xml.etree.ElementTree as ET

def load_pcap(file_path):
    try:
        return rdpcap(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def load_xml(file_path):
    try:
        tree = ET.parse(file_path)
        return tree.getroot()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def find_unencrypted_data(packets, keywords, file_name, xml_data):
    found_data = False
    for i, packet in enumerate(packets):
        if TCP in packet and packet[TCP].payload:
            payload = str(packet[TCP].payload)
            for keyword in keywords:
                if re.search(keyword, payload, re.IGNORECASE):
                    if xml_data and check_xml_tag(xml_data[i], 'suspicious'):
                        print(f"Unencrypted {keyword} found in suspicious {file_name}")
                    else:
