#!/usr/bin/env python
"""
Quick Startup Script - USB Security Monitoring
Run this to start both Django and the monitor
"""

import subprocess
import time
import sys
import os
import requests
from pathlib import Path

def main():
    print("\n")
    print("╔" + "="*56 + "╗")
    print("║  USB SECURITY MONITORING - QUICK START                  ║")
    print("║  Starting all required components...                    ║")
    print("╚" + "="*56 + "╝")
    print()
    
    # Get project root
    root = Path(__file__).parent.absolute()
    backend_dir = root / "backend"
    scripts_dir = backend_dir / "scripts"
    
    print(f"[*] Project root: {root}")
    print(f"[*] Backend dir: {backend_dir}")
    
    if not backend_dir.exists():
        print("[-] Backend directory not found!")
        return 1
    
    # Get Python executable
    venv_python = root / ".venv" / "Scripts" / "python.exe"
    
    if sys.platform == "win32":
        venv_python_alt = root / ".venv" / "Scripts" / "python"
    else:
        venv_python = root / ".venv" / "bin" / "python"
        venv_python_alt = None
    
    if not venv_python.exists():
        print(f"[-] Python not found at: {venv_python}")
        return 1
    
    print(f"[+] Python found: {venv_python}")
    print()
    
    # Start Django
    print("[*] Starting Django backend...")
    print("[*] URL: http://127.0.0.1:8000")
    print()
    
    try:
        if sys.platform == "win32":
            # Windows - open in new cmd window
            django_cmd = [
                "start",
                "/B",
                "cmd",
                "/c",
                f"{venv_python} manage.py runserver"
            ]
            # Use shell=True for start command
            django_proc = subprocess.Popen(
                django_cmd,
                cwd=str(backend_dir),
                shell=True
            )
        else:
            # Unix/Linux
            django_proc = subprocess.Popen(
                [str(venv_python), "manage.py", "runserver"],
                cwd=str(backend_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    except Exception as e:
        print(f"[-] Failed to start Django: {e}")
        return 1
    
    print("[+] Django started")
    print("[*] Waiting for Django to be ready...")
    
    # Wait for Django
    for attempt in range(10):
        try:
            response = requests.get("http://127.0.0.1:8000/api/security/event/", timeout=2)
            print("[+] Django backend is responding!")
            break
        except:
            if attempt == 9:
                print("[-] Django startup timeout")
                return 1
            time.sleep(1)
    
    print()
    print("[*] Starting USB Security Monitor...")
    
    try:
        if sys.platform == "win32":
            # Windows - open in new cmd window
            monitor_cmd = [
                "start",
                "cmd",
                "/c",
                f"{venv_python} smart_usb_monitor.py"
            ]
            monitor_proc = subprocess.Popen(
                monitor_cmd,
                cwd=str(scripts_dir),
                shell=True
            )
        else:
            # Unix/Linux
            monitor_proc = subprocess.Popen(
                [str(venv_python), "smart_usb_monitor.py"],
                cwd=str(scripts_dir)
            )
    except Exception as e:
        print(f"[-] Failed to start monitor: {e}")
        return 1
    
    print("[+] Monitor started")
    print()
    
    print("╔" + "="*56 + "╗")
    print("║  ✅ SYSTEM STARTED SUCCESSFULLY!                         ║")
    print("║                                                         ║")
    print("║  🌐 Django Backend:   http://127.0.0.1:8000             ║")
    print("║  📡 Monitor Status:   Running                           ║")
    print("║  📸 Camera:           Ready                             ║")
    print("║  💾 Database:         Connected                         ║")
    print("║                                                         ║")
    print("║  ⚠️  INSERT A USB DEVICE TO BEGIN MONITORING!            ║")
    print("║                                                         ║")
    print("║  Check logs:                                            ║")
    print("║  - Monitor window (separate CMD window)                 ║")
    print("║  - Photos: backend/scripts/security_captures/          ║")
    print("║  - API: http://127.0.0.1:8000/api/security/event/     ║")
    print("║                                                         ║")
    print("║  Close this window to keep monitoring running.          ║")
    print("║  Both Django and Monitor will continue in background.   ║")
    print("╚" + "="*56 + "╝")
    print()
    
    # Keep main process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        django_proc.terminate()
        monitor_proc.terminate()
        print("[+] System stopped")
        return 0

if __name__ == "__main__":
    sys.exit(main())
