#!/usr/bin/env python
"""
START USB MONITORING - With Proper Path Handling
This script starts the USB monitor with correct directory handling
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def main():
    # Get script directory (where this file is)
    script_dir = Path(__file__).parent.absolute()
    backend_dir = script_dir / "backend"
    scripts_dir = backend_dir / "scripts"
    monitor_script = scripts_dir / "smart_usb_monitor.py"
    
    print("\n" + "="*70)
    print("📱 USB & MOBILE DEVICE MONITOR - STARTUP")
    print("="*70)
    print(f"\nProject Root: {script_dir}")
    print(f"Backend Dir:  {backend_dir}")
    print(f"Scripts Dir:  {scripts_dir}")
    print(f"Monitor Script: {monitor_script}")
    
    # Verify monitor script exists
    if not monitor_script.exists():
        print(f"\n✗ ERROR: Monitor script not found!")
        print(f"  Expected: {monitor_script}")
        return 1
    
    print(f"\n✓ Monitor script found")
    
    # Check if Django is running
    print("\n[*] Checking Django backend status...")
    try:
        import requests
        response = requests.get('http://127.0.0.1:8000/api/security/event/', timeout=2)
        print(f"✓ Django is running (status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"⚠ Django doesn't appear to be running on port 8000")
        print(f"\nTo start Django in another terminal:")
        print(f"  cd backend")
        print(f"  python manage.py runserver")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return 1
    except Exception as e:
        print(f"⚠ Could not verify Django: {e}")
    
    # Create required directories
    print("\n[*] Setting up directories...")
    security_captures = scripts_dir / "security_captures"
    known_faces = scripts_dir / "known_faces"
    
    for directory in [security_captures, known_faces]:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created: {directory}")
        else:
            print(f"  ✓ Exists: {directory}")
    
    # Start monitor
    print("\n" + "="*70)
    print("🚀 STARTING USB MONITOR")
    print("="*70)
    print(f"\nCommand: python {monitor_script}")
    print(f"Working directory: {scripts_dir}")
    print(f"\nMonitor is starting in current terminal...")
    print("To stop monitoring: Press Ctrl+C")
    print("\n" + "-"*70 + "\n")
    
    # Run monitor from scripts directory
    try:
        os.chdir(scripts_dir)
        subprocess.run([sys.executable, str(monitor_script)])
    except KeyboardInterrupt:
        print("\n\n[*] Monitor stopped by user")
        return 0
    except Exception as e:
        print(f"\n✗ Error running monitor: {e}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
