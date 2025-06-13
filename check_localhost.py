#!/usr/bin/env python3
"""
Check what's running on localhost ports and fix critical issues.
"""

import subprocess
import os
from pathlib import Path


def check_ports():
    """Check what's running on common ports."""
    print("🔍 Checking localhost ports...")

    ports_to_check = [3000, 5173, 8000, 8080, 5432]

    for port in ports_to_check:
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}"], capture_output=True, text=True
            )

            if result.stdout.strip():
                print(f"\n📍 Port {port} is in use:")
                lines = result.stdout.strip().split("\n")
                for line in lines[1:]:  # Skip header
                    parts = line.split()
                    if len(parts) >= 2:
                        process = parts[0]
                        pid = parts[1]
                        print(f"   Process: {process} (PID: {pid})")
            else:
                print(f"✅ Port {port} is available")

        except Exception as e:
            print(f"⚠️  Could not check port {port}: {e}")


def kill_port_8000():
    """Kill processes on port 8000."""
    print("\n🔧 Cleaning up port 8000...")

    try:
        result = subprocess.run(
            ["lsof", "-ti", ":8000"], capture_output=True, text=True
        )

        if result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            print(f"Found {len(pids)} process(es) on port 8000")

            for pid in pids:
                try:
                    subprocess.run(["kill", "-9", pid], check=True)
                    print(f"✅ Killed process {pid}")
                except subprocess.CalledProcessError:
                    print(f"⚠️  Could not kill process {pid}")
        else:
            print("✅ Port 8000 is already clean")

    except Exception as e:
        print(f"⚠️  Error cleaning port 8000: {e}")


def check_backend_status():
    """Check if backend can start."""
    print("\n🧪 Testing backend import...")

    backend_dir = Path("pme_calculator/backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False

    # Change to backend directory
    original_dir = os.getcwd()
    try:
        os.chdir(backend_dir)

        # Test basic import
        try:
            from analysis_engine import PMEAnalysisEngine

            print("✅ PMEAnalysisEngine import successful")
            return True
        except ImportError as e:
            print(f"❌ Import error: {e}")
            return False

    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False
    finally:
        os.chdir(original_dir)


def check_frontend_status():
    """Check frontend status."""
    print("\n🧪 Checking frontend...")

    frontend_dir = Path("pme_calculator/frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False

    package_json = frontend_dir / "package.json"
    if package_json.exists():
        print("✅ Frontend directory found with package.json")

        # Check if node_modules exists
        node_modules = frontend_dir / "node_modules"
        if node_modules.exists():
            print("✅ node_modules directory exists")
        else:
            print("⚠️  node_modules not found - run 'npm install'")

        return True
    else:
        print("❌ package.json not found in frontend directory")
        return False


def provide_startup_instructions():
    """Provide clear startup instructions."""
    print("\n" + "=" * 50)
    print("🚀 STARTUP INSTRUCTIONS")
    print("=" * 50)

    print("\n1. 🔧 FIRST: Clean up any running processes")
    print("   Run this script to kill port conflicts")

    print("\n2. 🖥️  START BACKEND:")
    print("   cd pme_calculator/backend")
    print("   python3 main_minimal.py")
    print("   ➜ Should start on: http://localhost:8000")

    print("\n3. 🌐 START FRONTEND (in new terminal):")
    print("   cd pme_calculator/frontend")
    print("   npm install  # if node_modules missing")
    print("   npm run dev")
    print("   ➜ Should start on: http://localhost:5173")

    print("\n4. 🌍 ACCESS APPLICATION:")
    print("   Frontend: http://localhost:5173")
    print("   Backend API: http://localhost:8000/api/docs")
    print("   Health Check: http://localhost:8000/api/health")


def main():
    """Main diagnostic function."""
    print("🔍 PME Calculator Localhost Diagnostic")
    print("=" * 50)

    # Check what's running
    check_ports()

    # Clean up port 8000
    kill_port_8000()

    # Check backend
    backend_ok = check_backend_status()

    # Check frontend
    frontend_ok = check_frontend_status()

    # Provide instructions
    provide_startup_instructions()

    # Summary
    print("\n📊 SYSTEM STATUS:")
    print(f"   Backend Ready: {'✅' if backend_ok else '❌'}")
    print(f"   Frontend Ready: {'✅' if frontend_ok else '❌'}")

    if not backend_ok:
        print("\n⚠️  Backend issues detected. Check import errors above.")

    if not frontend_ok:
        print("\n⚠️  Frontend issues detected. Check directory structure.")

    if backend_ok and frontend_ok:
        print("\n🎉 System appears ready! Follow startup instructions above.")


if __name__ == "__main__":
    main()
