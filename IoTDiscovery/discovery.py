from scapy.all import ARP, Ether, srp
from mac_vendor_lookup import MacLookup
import socket
import csv
from collections import Counter
import matplotlib.pyplot as plt

def scan_ports(ip, ports=[80, 443, 1883, 8080, 8000]):
    open_ports = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex((ip, port)) == 0:
                    open_ports.append(port)
        except Exception:
            pass
    return open_ports

def discover_devices(network_range):
    try:
        arp = ARP(pdst=network_range)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp

        result = srp(packet, timeout=2, verbose=0)[0]

        devices = []
        for _, received in result:
            device_info = {
                "ip": received.psrc,
                "mac": received.hwsrc
            }
            try:
                device_info["vendor"] = MacLookup().lookup(device_info["mac"])
            except Exception:
                device_info["vendor"] = "Unknown"
            device_info["open_ports"] = scan_ports(device_info["ip"])
            devices.append(device_info)

        return devices
    except KeyboardInterrupt:
        print("\nScan interrupted.")
        sys.exit()

def save_to_csv(devices, filename="devices.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["IP Address", "MAC Address", "Vendor", "Open Ports"])
        for device in devices:
            writer.writerow([
                device["ip"],
                device["mac"],
                device["vendor"],
                ", ".join(map(str, device["open_ports"]))
            ])

def visualize_vendors(devices):
    vendor_counts = Counter(device["vendor"] for device in devices)
    labels, sizes = zip(*vendor_counts.items())

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
    plt.title("IoT Devices by Vendor")
    plt.show()

if __name__ == "__main__":
    print("IoT Device Discovery")
    network_range = input("Enter your network range (e.g., 192.168.1.0/24): ")

    print("\nScanning network...")
    devices = discover_devices(network_range)

    if devices:
        print("\nDiscovered Devices:")
        print("{:<20} {:<20} {:<20} {:<20}".format("IP Address", "MAC Address", "Vendor", "Open Ports"))
        print("-" * 80)
        for device in devices:
            open_ports = ", ".join(map(str, device["open_ports"]))
            print("{:<20} {:<20} {:<20} {:<20}".format(device["ip"], device["mac"], device["vendor"], open_ports))
        
        # Save results to a CSV file
        save_to_csv(devices, filename="devices.csv")
        print("\nResults saved to devices.csv")
        
        # Visualize the vendor distribution
        visualize_vendors(devices)
    else:
        print("No devices found.")
