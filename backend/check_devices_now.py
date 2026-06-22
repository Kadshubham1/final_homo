#!/usr/bin/env python
"""
INSTANT DEVICE CHECK - Shows what devices are connected RIGHT NOW
"""

import os
import sys

try:
    import wmi
    import pythoncom
except:
    print("ERROR: wmi missing. Run: pip install wmi")
    sys.exit(1)

print("="*70)
print("🔍 CHECKING CONNECTED DEVICES NOW")
print("="*70)

pythoncom.CoInitialize()
try:
    c = wmi.WMI()
    
    print("\n[1] USB DRIVES:")
    drives = list(c.Win32_LogicalDisk(DriveType=2))
    if drives:
        for d in drives:
            print(f"    Device: {d.DeviceID}")
            print(f"    Label: {d.VolumeName}")
            print(f"    Serial: {d.VolumeSerialNumber}")
            print(f"    Total: {d.Size} bytes")
    else:
        print("    (No USB drives detected)")
    
    print("\n[2] PORTABLE DEVICES (Phones, etc):")
    portables = []
    for device in c.Win32_PnPEntity(ConfigManagerErrorCode=0):
        try:
            name = getattr(device, 'Name', '')
            pnp_class = getattr(device, 'PNPClass', '')
            
            if pnp_class == "WPD" or "Portable" in name or "Phone" in name or "Mobile" in name:
                portables.append(name)
                print(f"    - {name}")
        except:
            pass
    
    if not portables:
        print("    (No portable devices detected)")
    
    print("\n[3] ALL USB DEVICES:")
    try:
        usb_devices = list(c.Win32_USBDevice())
        print(f"    Found {len(usb_devices)} USB devices total")
    except:
        print("    (USBDevice info not available)")
    
    print("\n" + "="*70)
    print("SUMMARY:")
    print(f"  USB Drives: {len(drives)}")
    print(f"  Portable Devices: {len(portables)}")
    print("="*70)
    
    if len(drives) == 0 and len(portables) == 0:
        print("\n⚠️  NO DEVICES CONNECTED")
        print("\nTo create logs:")
        print("  1. Connect your mobile device via USB cable")
        print("  2. Set phone to 'File Transfer' / 'MTP' mode")
        print("  3. Unlock your phone when prompted")
        print("  4. Then run the monitor again")
        sys.exit(1)
    else:
        print("\n✓ Devices are connected!")
        print("If monitor is running, it should detect these and create logs.")

finally:
    pythoncom.CoUninitialize()
