#!/usr/bin/env python3
"""
DNHBRIXX Hotspot Watch
Real-time hotspot device monitor with GUI, CSV export, and device alerts.
Created by DNHBRIXX
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re
import csv
import threading
import time
import winsound
import urllib.request
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

APP_NAME = "DNHBRIXX Hotspot Watch"
APP_VERSION = "1.0.0"
CREATOR = "Created by DNHBRIXX"
COLOR_DARK_BG = "#0a0e27"
COLOR_SECONDARY_BG = "#101a35"
COLOR_ACCENT = "#3ddc97"
COLOR_DANGER = "#ff6b6b"
COLOR_INFO = "#5fa8ff"
COLOR_TEXT = "#f5f7ff"
COLOR_TEXT_DIM = "#a8b8d8"
COLOR_SCANNING = "#7ef2bf"

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

def get_vendor(mac):
    """Get vendor from MAC address prefix."""
    mac_upper = mac.upper()
    for prefix, vendor in VENDOR_MAP.items():
        if mac_upper.startswith(prefix):
            return vendor
    return "Unknown"

def get_device_name(mac, vendor):
    """Guess device name based on vendor."""
    device_names = {
        "Apple": "Apple Device",
        "Samsung": "Samsung Device",
        "Xiaomi": "Xiaomi Device",
        "HUAWEI": "HUAWEI Device",
        "OnePlus": "OnePlus Device",
        "Motorola": "Motorola Device",
        "LG": "LG Device",
        "Sony": "Sony Device",
        "OPPO": "OPPO Device",
    }
    return device_names.get(vendor, f"{vendor} Device")

def scan_network_arp():
    """Scan network using ARP command."""
    try:
        if subprocess.sys.platform == "win32":
            result = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception:
        return ""

def scan_network_ip_neigh():
    """Scan network using ip neigh command (Linux/macOS)."""
    try:
        result = subprocess.run(["ip", "neigh"], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception:
        return ""

def parse_devices(output):
    """Parse ARP or ip neigh output to extract devices."""
    devices = []
    lines = output.splitlines()
    
    for line in lines:
        match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f:-]+)', line)
        if match:
            ip = match.group(1)
            mac = match.group(2).upper()
            
            if mac == "FF:FF:FF:FF:FF:FF" or ip.startswith("255."):
                continue
            
            vendor = get_vendor(mac)
            name = get_device_name(mac, vendor)
            
            devices.append({
                "ip": ip,
                "mac": mac,
                "vendor": vendor,
                "name": name,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    return devices

def scan_network():
    """Main network scan function."""
    # Try ARP first
    output = scan_network_arp()
    if output:
        return parse_devices(output)
    
    # Fallback to ip neigh
    output = scan_network_ip_neigh()
    if output:
        return parse_devices(output)
    
    return []

def play_alert_sound():
    """Play alert sound for new device."""
    try:
        if subprocess.sys.platform == "win32":
            winsound.Beep(1000, 500)  # 1000Hz, 500ms
        else:
            # For Linux/macOS, use system bell or other method
            import os
            os.system('afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || echo -e "\\a"')
    except Exception:
        pass

class AnimatedSpinner:
    """Animated spinner for scanning status."""
    def __init__(self):
        self.frames = ['◐', '◓', '◑', '◒']
        self.index = 0
    
    def get_frame(self):
        self.index = (self.index + 1) % len(self.frames)
        return self.frames[self.index]

class HotspotWatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1200x700")
        self.root.configure(bg=COLOR_DARK_BG)
        self.root.resizable(True, True)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Treeview', background=COLOR_SECONDARY_BG, foreground=COLOR_TEXT, fieldbackground=COLOR_SECONDARY_BG, borderwidth=0)
        self.style.configure('Treeview.Heading', background=COLOR_SECONDARY_BG, foreground=COLOR_ACCENT, borderwidth=0)
        self.style.map('Treeview', background=[('selected', COLOR_ACCENT)])
        self.style.map('Treeview.Heading', background=[('active', COLOR_ACCENT)])
        
        self.devices = []
        self.previous_devices = set()
        self.current_devices = set()
        self.running = False
        self.scan_thread = None
        self.spinner = AnimatedSpinner()
        self.scan_count = 0
        
        self.build_ui()
        self.style_configure()
    
    def style_configure(self):
        """Configure custom styles."""
        style = ttk.Style()
        style.configure('TFrame', background=COLOR_DARK_BG)
        style.configure('TLabel', background=COLOR_DARK_BG, foreground=COLOR_TEXT)
    
    def build_ui(self):
        """Build the user interface."""
        # Header
        header = tk.Frame(self.root, bg=COLOR_SECONDARY_BG, height=90)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        title = tk.Label(header, text=APP_NAME, font=("Segoe UI", 26, "bold"), fg=COLOR_ACCENT, bg=COLOR_SECONDARY_BG)
        title.pack(pady=(12, 0))
        
        info = tk.Label(header, text=f"{CREATOR} | v{APP_VERSION}", font=("Segoe UI", 9, "italic"), fg=COLOR_TEXT_DIM, bg=COLOR_SECONDARY_BG)
        info.pack(pady=(2, 12))
        
        # Controls
        controls = tk.Frame(self.root, bg=COLOR_SECONDARY_BG, height=70)
        controls.pack(fill=tk.X, padx=16, pady=(16, 12))
        controls.pack_propagate(False)
        
        button_frame = tk.Frame(controls, bg=COLOR_SECONDARY_BG)
        button_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.start_btn = tk.Button(
            button_frame, text="▶ Start Scan", command=self.start_scan,
            bg=COLOR_ACCENT, fg="#05160d", font=("Segoe UI", 11, "bold"),
            width=18, height=2, relief="flat", cursor="hand2"
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(
            button_frame, text="⏹ Stop", command=self.stop_scan,
            bg=COLOR_DANGER, fg=COLOR_TEXT, font=("Segoe UI", 11, "bold"),
            width=12, height=2, relief="flat", cursor="hand2"
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_btn = tk.Button(
            button_frame, text="💾 Export CSV", command=self.export_csv,
            bg=COLOR_INFO, fg="#081826", font=("Segoe UI", 11, "bold"),
            width=16, height=2, relief="flat", cursor="hand2"
        )
        self.export_btn.pack(side=tk.LEFT)
        
        status_frame = tk.Frame(controls, bg=COLOR_SECONDARY_BG)
        status_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        status_label = tk.Label(status_frame, text="Status:", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_DIM, bg=COLOR_SECONDARY_BG)
        status_label.pack(side=tk.LEFT)
        
        self.status_value = tk.Label(status_frame, text="● Idle", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=COLOR_SECONDARY_BG)
        self.status_value.pack(side=tk.LEFT, padx=(8, 20))
        
        devices_label = tk.Label(status_frame, text="Devices:", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_DIM, bg=COLOR_SECONDARY_BG)
        devices_label.pack(side=tk.LEFT)
        
        self.device_count = tk.Label(status_frame, text="0", font=("Segoe UI", 10, "bold"), fg=COLOR_ACCENT, bg=COLOR_SECONDARY_BG)
        self.device_count.pack(side=tk.LEFT, padx=(8, 0))
        
        # Table
        table_frame = tk.Frame(self.root, bg=COLOR_DARK_BG)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))
        
        columns = ("ip", "mac", "vendor", "name", "time")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("ip", text="IP Address")
        self.tree.heading("mac", text="MAC Address")
        self.tree.heading("vendor", text="Vendor")
        self.tree.heading("name", text="Device Name")
        self.tree.heading("time", text="Last Seen")
        
        self.tree.column("ip", width=140, anchor="center")
        self.tree.column("mac", width=170, anchor="center")
        self.tree.column("vendor", width=120, anchor="center")
        self.tree.column("name", width=200, anchor="center")
        self.tree.column("time", width=180, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Footer
        footer = tk.Frame(self.root, bg=COLOR_SECONDARY_BG, height=50)
        footer.pack(fill=tk.X, padx=0, pady=0)
        footer.pack_propagate(False)
        
        self.spinner_label = tk.Label(footer, text="", font=("Segoe UI", 10, "bold"), fg=COLOR_SCANNING, bg=COLOR_SECONDARY_BG)
        self.spinner_label.pack(side=tk.LEFT, padx=(16, 0), pady=10)
        
        info_text = tk.Label(footer, text="Real-time device monitoring • Non-root • No app detection", font=("Segoe UI", 9, "italic"), fg=COLOR_TEXT_DIM, bg=COLOR_SECONDARY_BG)
        info_text.pack(side=tk.RIGHT, padx=(0, 16), pady=10)
    
    def start_scan(self):
        """Start scanning the network."""
        if self.running:
            return
        
        self.running = True
        self.previous_devices = self.current_devices.copy()
        self.status_value.config(text="● Scanning", fg=COLOR_ACCENT)
        self.scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
        self.scan_thread.start()
    
    def stop_scan(self):
        """Stop scanning the network."""
        self.running = False
        self.status_value.config(text="● Stopped", fg=COLOR_DANGER)
        self.spinner_label.config(text="")
    
    def scan_loop(self):
        """Main scanning loop."""
        while self.running:
            self.update_spinner()
            devices = scan_network()
            self.devices = devices
            self.current_devices = set((d["ip"], d["mac"]) for d in devices)
            
            # Check for new devices
            new_devices = self.current_devices - self.previous_devices
            if new_devices and self.scan_count > 0:  # Skip first scan
                play_alert_sound()
                self.root.after(0, self.show_new_device_alert, len(new_devices))
            
            self.previous_devices = self.current_devices.copy()
            self.scan_count += 1
            
            self.root.after(0, self.refresh_table)
            time.sleep(5)  # Scan every 5 seconds
    
    def update_spinner(self):
        """Update the animated spinner."""
        frame = self.spinner.get_frame()
        self.root.after(0, lambda: self.spinner_label.config(text=f"{frame} Scanning..."))
        time.sleep(0.2)
    
    def refresh_table(self):
        """Refresh the device table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, device in enumerate(self.devices):
            self.tree.insert("", "end", values=(
                device["ip"],
                device["mac"],
                device["vendor"],
                device["name"],
                device["time"]
            ))
        
        self.device_count.config(text=str(len(self.devices)))
    
    def show_new_device_alert(self, count):
        """Show alert for new devices detected."""
        messagebox.showinfo(
            "New Device(s) Detected",
            f"🔔 {count} new device(s) joined the hotspot!"
        )
    
    def export_csv(self):
        """Export devices to CSV file."""
        if not self.devices:
            messagebox.showwarning("No Data", "No device data available to export.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = Path(f"hotspot_devices_{timestamp}.csv")
        
        try:
            with file_path.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["IP Address", "MAC Address", "Vendor", "Device Name", "Last Seen"])
                writer.writeheader()
                for d in self.devices:
                    writer.writerow({
                        "IP Address": d["ip"],
                        "MAC Address": d["mac"],
                        "Vendor": d["vendor"],
                        "Device Name": d["name"],
                        "Last Seen": d["time"]
                    })
            
            messagebox.showinfo(
                "Export Complete",
                f"✓ CSV exported successfully!\n\nFile: {file_path.name}\nLocation: {file_path.resolve()}"
            )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV:\n{str(e)}")

def main():
    root = tk.Tk()
    app = HotspotWatchApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
