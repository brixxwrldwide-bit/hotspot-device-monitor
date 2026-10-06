# ( NOISY ) privacy and anonymity

**Real-time hotspot device monitor with beautiful GUI, CSV export, and device alerts**

*Created by DNHBRIXX*

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## Features

✅ **Real-time Device Monitoring**
- Live scan of connected hotspot devices
- Automatic network detection every 5 seconds
- Clean, dark-themed GUI with animated spinner

✅ **Device Information**
- IP Address detection
- MAC Address identification
- Vendor/Brand recognition (Apple, Samsung, Xiaomi, etc.)
- Device name prediction
- Last seen timestamp

✅ **Alerts & Notifications**
- 🔔 Audio alert when new devices join
- Desktop notification pop-ups
- Real-time device count tracking

✅ **CSV Export**
- Export all detected devices to CSV
- Timestamped file naming
- Full device information included

✅ **Non-Root Compatible**
- Works without administrator privileges
- Cross-platform (Windows, Linux, macOS)
- Uses standard ARP/IP neighbor discovery

---

## What It Can Do

| Feature | Capability |
|---------|------------|
| Detect connected devices | ✅ Yes |
| Show IP & MAC addresses | ✅ Yes |
| Identify device vendor/brand | ✅ Yes |
| Show device names | ✅ Yes |
| Bandwidth monitoring | ⚠️ Limited |
| See visited websites | ❌ No (HTTPS encrypted) |
| Detect running apps | ❌ No (requires root) |
| Read messages/chats | ❌ No (privacy encrypted) |

---

## Installation

### Requirements
- Python 3.7 or higher
- tkinter (usually included with Python)
- Windows/Linux/macOS

### Setup

```bash
# Clone the repository
git clone https://github.com/brixxwrldwide-bit/hotspot-device-monitor.git
cd hotspot-device-monitor

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Run the Application

```bash
python hotspot_watch.py
```

### How to Use

1. **Start Scan** - Click "▶ Start Scan" to begin monitoring
2. **Monitor Devices** - Watch the live table of connected devices
3. **Listen for Alerts** - New device joins = 🔔 sound alert + notification
4. **Export Data** - Click "💾 Export CSV" to save device list
5. **Stop Scan** - Click "⏹ Stop" to pause monitoring

---

## UI Overview

```
┌─────────────────────────────────────────────────────────┐
│  DNHBRIXX Hotspot Watch v1.0.0                         │
│  Created by DNHBRIXX                                   │
├─────────────────────────────────────────────────────────┤
│  [▶ Start] [⏹ Stop] [💾 Export]  Status: ● Idle        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  IP Address | MAC Address | Vendor | Name | Last Seen │
│  ─────────────────────────────────────────────────────  │
│  192.168... | AA:BB:CC... | Apple  | ... | 14:23:15  │
│  192.168... | DD:EE:FF... | Samsung| ... | 14:23:18  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  ◐ Scanning... │ Real-time monitoring • Non-root      │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration

### Vendor Detection

Edit `VENDOR_MAP` in `hotspot_watch.py` to add more device vendors:

```python
VENDOR_MAP = {
    "00:1A:11": "Apple",
    "00:26:01": "Samsung",
    # Add more MAC prefixes here
}
```

### Scan Interval

Change scan frequency in the `scan_loop()` method:

```python
time.sleep(5)  # Scan every 5 seconds (default)
time.sleep(3)  # Scan every 3 seconds (faster)
```

---

## Troubleshooting

### No devices detected?

1. Make sure you're connected to a hotspot
2. Check your network connection
3. On Linux/macOS, you may need `sudo` for full ARP table access

### Sound alerts not working?

- Windows: Should work out of the box
- Linux: Install `paplay` or `afplay`
- macOS: Requires system sounds enabled

### Export CSV not saving?

- Check folder permissions
- Ensure disk space is available
- Try a different location

---

## Technical Details

### How It Works

1. **ARP Scanning**: Uses `arp -a` or `ip neigh` to detect active devices
2. **MAC Lookup**: Identifies device vendors by MAC address prefix
3. **Device Naming**: Predicts device names based on vendor
4. **CSV Export**: Saves all data to timestamped CSV files
5. **Audio Alerts**: Plays system beep when new device joins

### Network Detection Methods

| Method | Platform | Privilege |
|--------|----------|----------|
| ARP -a | Windows/Unix | User |
| ip neigh | Linux | User |
| Fallback | All | User |

---

## Limitations

⚠️ **Without Root/Admin Access:**
- Cannot see app-level traffic
- Cannot intercept HTTPS traffic
- Cannot access device internals
- Only network-level visibility

⚠️ **Privacy & Ethics:**
- Only use on networks you control
- Respect user privacy
- Local laws may apply to network monitoring

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Check existing discussions
- Review the troubleshooting section

---

## Credits

**Creator:** DNHBRIXX

**Built with:** Python, Tkinter

**Last Updated:** 2026-10-05

---

*Made with ❤️ for network monitoring enthusiasts*
