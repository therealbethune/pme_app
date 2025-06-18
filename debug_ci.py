#!/usr/bin/env python3
"""Debug script to test CI environment setup"""

import sys
import subprocess
import time


def run_command(cmd, timeout=300):
    """Run a command with timeout"""
    print(f"Running: {cmd}")
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        duration = time.time() - start_time
        print(f"Duration: {duration:.2f}s")
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout}s")
        return False


def main():
    print("=== Python Environment Debug ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")

    print("\n=== System Info ===")
    run_command("uname -a")
    run_command("which python")
    run_command("which python3")
    run_command("which pip")
    run_command("which pip3")

    print("\n=== Package Installation Test ===")
    if not run_command("python3 -m pip install --upgrade pip tox", timeout=120):
        print("Failed to install pip and tox")
        return False

    print("\n=== Tox Environment Test ===")
    if not run_command("tox --version"):
        print("Failed to get tox version")
        return False

    print("\n=== Tox List Environments ===")
    if not run_command("tox -l"):
        print("Failed to list tox environments")
        return False

    print("\n=== Quick Setup Test ===")
    if not run_command("tox -e typecheck --notest", timeout=180):
        print("Failed to setup typecheck environment")
        return False

    print("\n=== All tests passed! ===")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
