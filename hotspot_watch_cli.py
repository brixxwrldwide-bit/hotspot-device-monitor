#!/usr/bin/env python3
"""
DNHBRIXX Hotspot Watch - CLI version
Works on Termux / Android / Linux terminal.
No Tkinter required.
Created by DNHBRIXX
"""

import argparse
import csv
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

APP_NAME = "DNHBRIXX Hotspot Watch"
APP_VERSION = "1.0.0 CLI"
CREATOR = "Created by DNHBRIXX"

VENDOR_MAP = {
    "00:1A:11": "Apple",
    "00:17:AB": "Apple",
    "00:26:01": "Samsung",
    "A4:5E:60": "Samsung",
    "F8:1A:67": "Android Device",
    "48:2C:6A": "Xiaomi",
    "34:23:BA": "Samsung",
    "94:3C:C6": "HUAWEI",
    "00:50:56": "VMware",
    "00:0C:29": "VMware",
    "10:52:1C": "Motorola",
    "44:6D:6C": "OnePlus",
    "2C:3E:CF": "Apple",
    "C8:3A:6B": "Sony",
    "7C:2C:BD": "LG",
    "B0:35:9F": "OPPO",
    "54:60:09": "Realtek",
}


def clear_screen():
    os.system("clear") if os.name != "nt" else os.system("cls")


def vendor_from_mac(mac):
    mac_upper = mac.upper()
    for prefix, vendor in VENDOR_MAP.items():
        if mac_upper.startswith(prefix):
            return vendor
    return "Unknown"


def name_from_vendor(vendor):
    names = {
        "Apple": "Apple Device",
        "Samsung": "Samsung Device",
        "Xiaomi": "Xiaomi Device",
        "HUAWEI": "HUAWEI Device",
        "OnePlus": "OnePlus Device",
        "Motorola": "Motorola Device",
        "LG": "LG Device",
        "Sony": "Sony Device",
        "OPPO": "OPPO Device",
        "Android Device": "Android Device",
    }
    return names.get(vendor, f"{vendor} Device")


def run_command(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass
    return ""


def parse_devices(raw_output):
    devices = []
    for line in raw_output.splitlines():
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f:-]+)", line)
        if not match:
            continue
        ip = match.group(1)
        mac = match.group(2).upper()
        if mac in ["FF:FF:FF:FF:FF:FF"]:
            continue
        vendor = vendor_from_mac(mac)
        devices.append({
            "ip": ip,
            "mac": mac,
            "vendor": vendor,
            "name": name_from_vendor(vendor),
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    return devices


def scan_network():
    output = run_command(["arp", "-a"])
    if output:
        devices = parse_devices(output)
        if devices:
            return devices

    output = run_command(["ip", "neigh"])
    if output:
        devices = parse_devices(output)
        if devices:
            return devices

    return []


def export_csv(devices, file_path):
    out = Path(file_path)
    rows = []
    for d in devices:
        rows.append({
            "IP Address": d["ip"],
            "MAC Address": d["mac"],
            "Vendor": d["vendor"],
            "Device Name": d["name"],
            "Last Seen": d["last_seen"],
        })

    with out.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["IP Address", "MAC Address", "Vendor", "Device Name", "Last Seen"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV exported to: {out.resolve()}\n")


def print_table(devices):
    print("\n" + "=" * 120)
    print(f"{APP_NAME} | {APP_VERSION}")
    print(f"{CREATOR}")
    print(f"Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 120)
    print(f"{'IP':<15} {'MAC':<17} {'Vendor':<12} {'Device Name':<18} {'Last Seen':<20}")
    print("-" * 120)

    if not devices:
        print("No devices found.")
        print("-" * 120)
        return

    for d in devices:
        print(f"{d['ip']:<15} {d['mac']:<17} {d['vendor']:<12} {d['name']:<18} {d['last_seen']:<20}")

    print("-" * 120)


def scan_once():
    devices = scan_network()
    print_table(devices)


def scan_loop(interval, export_path=None):
    seen = set()
    while True:
        devices = scan_network()
        current = {(d["ip"], d["mac"]) for d in devices}

        new_devices = current - seen
        if seen and new_devices:
            print("\n[ALERT] New device detected:")
            for d in devices:
                if (d["ip"], d["mac"]) in new_devices:
                    print(f"  - {d['ip']} | {d['mac']} | {d['vendor']} | {d['name']}")

        seen = current
        clear_screen()
        print_table(devices)

        if export_path:
            export_csv(devices, export_path)

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description=f"{APP_NAME} - hotspot monitoring for Termux / Linux terminals")
    parser.add_argument("--once", action="store_true", help="Run one scan and exit")
    parser.add_argument("--interval", type=int, default=5, help="Scan interval in seconds (default: 5)")
    parser.add_argument("--export", type=str, default="", help="Optional CSV file path to export results")
    args = parser.parse_args()

    if args.once:
        scan_once()
        if args.export:
            devices = scan_network()
            export_csv(devices, args.export)
        return

    print(f"{APP_NAME} - {APP_VERSION}")
    print(f"Monitoring hotspot every {args.interval} seconds. Press Ctrl+C to stop.\n")

    try:
        scan_loop(args.interval, args.export if args.export else None)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
