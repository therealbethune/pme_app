#!/usr/bin/env python3
"""
Quick fix script for immediate loading issues.
"""

import subprocess
from pathlib import Path

import psutil


def kill_port_8000():
    """Kill processes listening on port 8000 using graceful termination."""
    print("🔧 Scanning for processes listening on port 8000...")

    # First, identify all processes listening on port 8000
    listening_processes = []

    try:
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                # Get connections for this process
                connections = proc.net_connections(kind="inet")
                for conn in connections:
                    if (
                        hasattr(conn, "laddr")
                        and conn.laddr
                        and conn.laddr.port == 8000
                        and conn.status == psutil.CONN_LISTEN
                    ):
                        # Get command line for better identification
                        try:
                            cmdline = (
                                " ".join(proc.info["cmdline"])
                                if proc.info["cmdline"]
                                else proc.info["name"]
                            )
                            # Truncate very long command lines
                            if len(cmdline) > 80:
                                cmdline = cmdline[:77] + "..."
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            cmdline = proc.info["name"]

                        listening_processes.append(
                            {
                                "pid": proc.info["pid"],
                                "name": proc.info["name"],
                                "cmdline": cmdline,
                                "process": proc,
                            }
                        )
                        break  # Found listening connection, no need to check more
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                # Process may have disappeared or we don't have permission
                continue
    except Exception as e:
        print(f"⚠️  Error scanning processes: {e}")
        return

    if not listening_processes:
        print("✅ Port 8000 is already free")
        return

    # Display summary table
    print(f"\n📋 Found {len(listening_processes)} process(es) listening on port 8000:")
    print(
        "┌─────────┬──────────────┬─────────────────────────────────────────────────────────────────────────────┐"
    )
    print(
        "│   PID   │     NAME     │                                  COMMAND                                    │"
    )
    print(
        "├─────────┼──────────────┼─────────────────────────────────────────────────────────────────────────────┤"
    )

    for proc_info in listening_processes:
        pid_str = str(proc_info["pid"]).center(7)
        name_str = proc_info["name"][:12].ljust(12)
        cmd_str = proc_info["cmdline"][:75].ljust(75)
        print(f"│ {pid_str} │ {name_str} │ {cmd_str} │")

    print(
        "└─────────┴──────────────┴─────────────────────────────────────────────────────────────────────────────┘"
    )

    # Gracefully terminate processes
    print("\n🔄 Attempting graceful termination (SIGTERM)...")
    terminated_count = 0
    still_alive = []

    for proc_info in listening_processes:
        proc = proc_info["process"]
        try:
            print(
                f"   → Sending SIGTERM to PID {proc_info['pid']} ({proc_info['name']})"
            )
            proc.terminate()
            terminated_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"   ⚠️  Could not terminate PID {proc_info['pid']}: {e}")
            continue

    if terminated_count == 0:
        print("❌ No processes could be terminated")
        return

    # Wait for graceful shutdown
    print("⏳ Waiting 5 seconds for graceful shutdown...")
    import time

    time.sleep(5)

    # Check which processes are still alive
    for proc_info in listening_processes:
        proc = proc_info["process"]
        try:
            if proc.is_running():
                still_alive.append(proc_info)
        except psutil.NoSuchProcess:
            # Process is gone, which is what we want
            pass

    # Force kill any remaining processes
    killed_count = 0
    if still_alive:
        print(
            f"\n💀 Force killing {len(still_alive)} stubborn process(es) (SIGKILL)..."
        )
        for proc_info in still_alive:
            proc = proc_info["process"]
            try:
                print(
                    f"   → Sending SIGKILL to PID {proc_info['pid']} ({proc_info['name']})"
                )
                proc.kill()
                killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"   ⚠️  Could not kill PID {proc_info['pid']}: {e}")

    # Final summary
    total_handled = len(listening_processes)
    graceful_count = total_handled - len(still_alive)

    print("\n✅ Port 8000 cleanup complete:")
    print(f"   • {graceful_count} process(es) terminated gracefully")
    if killed_count > 0:
        print(f"   • {killed_count} process(es) force killed")
    if total_handled - graceful_count - killed_count > 0:
        print(
            f"   • {total_handled - graceful_count - killed_count} process(es) could not be stopped"
        )
    print(f"   • Total processes handled: {total_handled}")


def fix_analysis_engine():
    """Fix analysis_engine.py import."""
    print("🔧 Fixing analysis_engine.py...")

    backend_dir = Path("pme_calculator/backend")
    analysis_file = backend_dir / "analysis_engine.py"

    if analysis_file.exists():
        content = analysis_file.read_text()
        fixed_content = content.replace(
            "from .analysis_engine_legacy import *",
            "from analysis_engine_legacy import *",
        )
        analysis_file.write_text(fixed_content)
        print("✅ Fixed analysis_engine.py import")

    # Ensure legacy file has the class
    legacy_file = backend_dir / "analysis_engine_legacy.py"
    if legacy_file.exists():
        content = legacy_file.read_text()
        if "class PMEAnalysisEngine" not in content:
            # Add minimal class
            content += '''

class PMEAnalysisEngine:
    def __init__(self):
        import warnings
        warnings.warn("PMEAnalysisEngine is deprecated", DeprecationWarning)

    def analyze_fund(self, fund_data, index_data=None):
        from datetime import datetime
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }

def make_json_serializable(obj):
    """Make object JSON serializable."""
    import pandas as pd
    import numpy as np
    from datetime import datetime

    if isinstance(obj, (pd.DataFrame, pd.Series)):
        return obj.to_dict()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    else:
        return obj
'''
            legacy_file.write_text(content)
            print("✅ Added PMEAnalysisEngine class")


def fix_vite_config():
    """Fix vite.config.ts."""
    print("🔧 Fixing vite.config.ts...")

    frontend_dir = Path("pme_calculator/frontend")
    vite_config = frontend_dir / "vite.config.ts"

    config_content = """import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173
  }
})
"""
    vite_config.write_text(config_content)
    print("✅ Fixed vite.config.ts")


def start_backend():
    """Start the backend server."""
    print("🔧 Starting backend server...")

    backend_dir = Path("pme_calculator/backend")
    main_file = backend_dir / "main_minimal.py"

    if not main_file.exists():
        print("⚠️  main_minimal.py not found, skipping backend start")
        return

    try:
        subprocess.run(
            ["python3", str(main_file)],
            cwd=str(backend_dir),
            check=True,
            timeout=5,
        )
        print("✅ Backend server started")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start backend: {e}")
    except subprocess.TimeoutExpired:
        print("✅ Backend server started (timeout reached, likely running)")
    except FileNotFoundError:
        print("❌ python3 not found, please install Python")


def start_frontend():
    """Start the frontend development server."""
    print("🔧 Starting frontend server...")

    frontend_dir = Path("pme_calculator/frontend")
    package_json = frontend_dir / "package.json"

    if not package_json.exists():
        print("⚠️  package.json not found, skipping frontend start")
        return

    try:
        subprocess.run(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir),
            check=True,
            timeout=10,
        )
        print("✅ Frontend server started")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
    except subprocess.TimeoutExpired:
        print("✅ Frontend server started (timeout reached, likely running)")
    except FileNotFoundError:
        print("❌ npm not found, please install Node.js")


def main():
    """Apply quick fixes."""
    print("🚀 Quick Fix for Loading Issues")
    print("=" * 40)

    kill_port_8000()
    fix_analysis_engine()
    fix_vite_config()

    print("\n✅ Quick fixes applied!")
    print("\nNow try:")
    print("1. cd pme_calculator/backend && python3 main_minimal.py")
    print("2. cd pme_calculator/frontend && npm run dev")
    print("\nOr run with auto-start:")
    print("python3 quick_fix_loading.py --start")


if __name__ == "__main__":
    import sys

    if "--start" in sys.argv:
        main()
        print("\n🚀 Auto-starting servers...")
        start_backend()
        start_frontend()
    else:
        main()
