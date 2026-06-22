#!/usr/bin/env python
"""
Test Script for Mobile Device Detection
Tests multiple methods to detect mobile phones/MTP devices
"""

import sys
import os
import wmi

def test_pnp_entity():
    """Test PnPEntity mobile device detection"""
    print("\n" + "="*60)
    print("TEST 1: Win32_PnPEntity (Plug and Play Devices)")
    print("="*60)
    
    try:
        c = wmi.WMI()
        print("[*] Searching for Portable Devices (WPD)...")
        
        found_devices = []
        for device in c.Win32_PnPEntity(ConfigManagerErrorCode=0):
            try:
                pnp_class = getattr(device, 'PNPClass', '')
                name = getattr(device, 'Name', '')
                device_id = getattr(device, 'PNPDeviceID', '')
                
                # Print ALL devices with relevant info
                if name:
                    print(f"\n  Device: {name}")
                    print(f"  PNP Class: {pnp_class}")
                    print(f"  Device ID: {device_id}")
                    
                    # Check if it's a mobile device
                    if pnp_class == "WPD" or "Portable Device" in name or "MTP" in name:
                        print(f"  ✓ MOBILE DEVICE DETECTED!")
                        found_devices.append((name, device_id))
            except Exception as e:
                continue
        
        if found_devices:
            print(f"\n✓ Found {len(found_devices)} mobile device(s)")
            for name, device_id in found_devices:
                print(f"  - {name}: {device_id}")
        else:
            print("\n✗ No mobile devices found via PnPEntity")
            
        return len(found_devices) > 0
    except Exception as e:
        print(f"✗ Error in PnPEntity test: {e}")
        return False

def test_usb_devices():
    """Test USB device detection"""
    print("\n" + "="*60)
    print("TEST 2: Win32_USBDevice (Direct USB Devices)")
    print("="*60)
    
    try:
        c = wmi.WMI()
        print("[*] Searching for USB devices...")
        
        found_devices = []
        keyword_results = {
            'phone': [],
            'mtp': [],
            'android': [],
            'iphone': [],
            'samsung': [],
            'mobile': [],
            'portable': []
        }
        
        count = 0
        for device in c.Win32_USBDevice():
            try:
                name = getattr(device, 'Name', '')
                device_id = getattr(device, 'PNPDeviceID', '')
                description = getattr(device, 'Description', '')
                
                if name:
                    count += 1
                    device_lower = (name + ' ' + description).lower()
                    
                    # Track keyword matches
                    for keyword in keyword_results.keys():
                        if keyword in device_lower:
                            keyword_results[keyword].append(name)
                    
                    # Only print potentially mobile devices
                    keywords = ['phone', 'mtp', 'android', 'iphone', 'samsung', 'mobile', 'portable']
                    is_mobile = any(keyword in device_lower for keyword in keywords)
                    
                    if is_mobile or count <= 10:  # Print first 10 regardless
                        print(f"\n  Device: {name}")
                        if description:
                            print(f"  Description: {description}")
                        print(f"  Device ID: {device_id}")
                        if is_mobile:
                            print(f"  ✓ LOOKS LIKE MOBILE DEVICE!")
                            found_devices.append((name, device_id))
            except Exception as e:
                continue
        
        print(f"\n[*] Devices found by keyword:")
        for keyword, devices in keyword_results.items():
            if devices:
                print(f"  {keyword}: {len(devices)} device(s)")
                for dev in devices[:3]:
                    print(f"    - {dev}")
        
        if found_devices:
            print(f"\n✓ Found {len(found_devices)} mobile-like USB device(s)")
        else:
            print(f"\n[*] Scanned {count} USB devices total")
            print("✗ No mobile devices found via USBDevice")
            
        return len(found_devices) > 0
    except Exception as e:
        print(f"✗ Error in USBDevice test: {e}")
        return False

def test_usb_storage_devices():
    """Test USB storage device detection"""
    print("\n" + "="*60)
    print("TEST 3: Win32_USBStorageDevice (USB Storage)")
    print("="*60)
    
    try:
        c = wmi.WMI()
        print("[*] Searching for USB storage devices...")
        
        found_devices = []
        count = 0
        for device in c.Win32_USBStorageDevice():
            try:
                name = getattr(device, 'Name', '')
                device_id = getattr(device, 'PNPDeviceID', '')
                description = getattr(device, 'Description', '')
                
                if name:
                    count += 1
                    device_lower = (name + ' ' + description).lower()
                    
                    print(f"\n  Device: {name}")
                    if description:
                        print(f"  Description: {description}")
                    print(f"  Device ID: {device_id}")
                    
                    # Check for mobile indicators
                    if any(keyword in device_lower for keyword in ['phone', 'mtp', 'android', 'mobile']):
                        print(f"  ✓ MOBILE DEVICE DETECTED!")
                        found_devices.append((name, device_id))
            except Exception as e:
                continue
        
        if found_devices:
            print(f"\n✓ Found {len(found_devices)} mobile storage device(s)")
        else:
            print(f"\n[*] Found {count} USB storage device(s) total")
            print("✗ No mobile devices found via USBStorageDevice")
            
        return len(found_devices) > 0
    except Exception as e:
        print(f"✗ Error in USBStorageDevice test: {e}")
        return False

def test_logical_disks():
    """Test logical disk detection (may show USB mass storage)"""
    print("\n" + "="*60)
    print("TEST 4: Win32_LogicalDisk (Logical Drives)")
    print("="*60)
    
    try:
        c = wmi.WMI()
        print("[*] Scanning logical disks...")
        
        count = 0
        for disk in c.Win32_LogicalDisk():
            try:
                drive_type = getattr(disk, 'DriveType', '')
                device_id = getattr(disk, 'DeviceID', '')
                volume_name = getattr(disk, 'VolumeName', '')
                serial = getattr(disk, 'VolumeSerialNumber', '')
                
                # Type 2 = Removable, 3 = Fixed
                if drive_type == 2:  # Removable
                    count += 1
                    print(f"\n  Drive: {device_id}")
                    if volume_name:
                        print(f"  Volume: {volume_name}")
                    print(f"  Serial: {serial}")
                    print(f"  Type: Removable (Type {drive_type})")
            except:
                continue
        
        if count > 0:
            print(f"\n✓ Found {count} removable disk(s)")
            print("[*] NOTE: Mobile devices may appear here as removable storage")
        else:
            print("\n✗ No removable disks found")
            
        return count > 0
    except Exception as e:
        print(f"✗ Error in LogicalDisk test: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("📱 MOBILE DEVICE DETECTION - DIAGNOSTIC TEST")
    print("="*60)
    print("\nThis test will scan your system for connected mobile devices")
    print("using multiple WMI detection methods.\n")
    
    print("⚠️  IMPORTANT: Make sure your mobile device is:")
    print("  1. Plugged in via USB")
    print("  2. Unlocked (if required by device)")
    print("  3. USB mode set to: MTP/File Transfer mode")
    print("  4. Any permission dialogs on device: ACCEPT\n")
    
    input("Press ENTER when ready to scan...")
    
    results = []
    results.append(("PnPEntity (WPD)", test_pnp_entity()))
    results.append(("USBDevice", test_usb_devices()))
    results.append(("USBStorageDevice", test_usb_storage_devices()))
    results.append(("LogicalDisk", test_logical_disks()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for method, found in results:
        status = "✓ PASS" if found else "✗ FAIL"
        print(f"{status}: {method}")
    
    if any(found for _, found in results):
        print("\n✓ Device detection working!")
        print("[*] Your monitor should be able to detect mobile devices.")
    else:
        print("\n✗ No mobile devices detected")
        print("\nTRY:")
        print("  1. Check USB cable connection")
        print("  2. Unlock your device")
        print("  3. Change to MTP mode in USB settings")
        print("  4. Check Device Manager for unknown devices")
        print("  5. Try a different USB port")
        print("  6. Install any vendor-specific USB drivers")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Test canceled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[!] Unexpected error: {e}")
        sys.exit(1)
