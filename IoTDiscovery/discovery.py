from scapy.all import ARP, Ether, srp
from mac_vendor_lookup import MacLookup
import sys

def discover_devices(network_range):
    try:
        # Create ARP request
        arp = ARP(pdst=network_range)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp

        # Send packet and receive responses
        result = srp(packet, timeout=2, verbose=0)[0]

        devices = []
        for _, received in result:
            device_info = {
                "ip": received.psrc,
                "mac": received.hwsrc
            }
            # Try to get vendor information
            try:
                device_info["vendor"] = MacLookup().lookup(device_info["mac"])
            except Exception:
                device_info["vendor"] = "Unknown"
            devices.append(device_info)

        return devices
    except KeyboardInterrupt:
        print("\nScan interrupted.")
        sys.exit()

if __name__ == "__main__":
    print("IoT Device Discovery")
    network_range = input("Enter your network range: ")

    print("\nScanning network...")
    devices = discover_devices(network_range)

    if devices:
        print("\nDiscovered Devices:")
        print("{:<20} {:<20} {:<20}".format("IP Address", "MAC Address", "Vendor"))
        print("-" * 60)
        for device in devices:
            print("{:<20} {:<20} {:<20}".format(device["ip"], device["mac"], device["vendor"]))
    else:
        print("No devices found.")
