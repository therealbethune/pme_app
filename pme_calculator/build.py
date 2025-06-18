#!/usr/bin/env python3
"""
Build script for PME Calculator
This script automates the entire build process:
1. Builds the React frontend
2. Packages the application with PyInstaller
3. Creates a distributable executable
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, shell=False):
    """Run a command and handle errors."""
    print(f"🔧 Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        # Always use shell=False for security
        if isinstance(cmd, str):
            import shlex

            cmd_list = shlex.split(cmd)
            result = subprocess.run(
                cmd_list,
                cwd=cwd,
                shell=False,
                check=True,
                capture_output=True,
                text=True,
            )
        else:
            result = subprocess.run(
                cmd, cwd=cwd, shell=False, check=True, capture_output=True, text=True
            )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def check_dependencies():
    """Check if required tools are installed."""
    print("🔍 Checking dependencies...")

    # Check Node.js and npm
    if not run_command(["node", "--version"]):
        print("❌ Node.js not found. Please install Node.js from https://nodejs.org/")
        return False

    if not run_command(["npm", "--version"]):
        print("❌ npm not found. Please install npm")
        return False

    # Check Python and PyInstaller
    if not run_command([sys.executable, "--version"]):
        print("❌ Python not found")
        return False

    try:
        import pyinstaller

        print(f"✅ PyInstaller found: {pyinstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        if not run_command([sys.executable, "-m", "pip", "install", "pyinstaller"]):
            return False

    print("✅ All dependencies found")
    return True


def build_frontend():
    """Build the React frontend."""
    print("\n📦 Building React frontend...")

    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False

    # Install dependencies if node_modules doesn't exist
    if not (frontend_dir / "node_modules").exists():
        print("📥 Installing npm dependencies...")
        if not run_command(["npm", "install"], cwd=frontend_dir):
            return False

    # Build the frontend
    print("🏗️ Building frontend for production...")
    if not run_command(["npm", "run", "build"], cwd=frontend_dir):
        return False

    # Verify dist directory was created
    dist_dir = frontend_dir / "dist"
    if not dist_dir.exists():
        print("❌ Frontend build failed - dist directory not found")
        return False

    print("✅ Frontend build completed successfully")
    return True


def build_executable():
    """Build the executable with PyInstaller."""
    print("\n🔨 Building executable with PyInstaller...")

    backend_dir = Path("backend")
    spec_file = backend_dir / "pme_calculator.spec"

    if not spec_file.exists():
        print("❌ PyInstaller spec file not found")
        return False

    # Clean previous builds
    dist_dir = backend_dir / "dist"
    build_dir = backend_dir / "build"

    if dist_dir.exists():
        print("🧹 Cleaning previous build...")
        shutil.rmtree(dist_dir)

    if build_dir.exists():
        shutil.rmtree(build_dir)

    # Run PyInstaller
    print("🚀 Running PyInstaller...")
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "pme_calculator.spec"]

    if not run_command(cmd, cwd=backend_dir):
        return False

    # Check if executable was created
    system = platform.system()
    if system == "Darwin":  # macOS
        executable_path = dist_dir / "PME Calculator.app"
        if executable_path.exists():
            print(f"✅ macOS app bundle created: {executable_path}")
        else:
            executable_path = dist_dir / "PME_Calculator"
            if executable_path.exists():
                print(f"✅ Executable created: {executable_path}")
            else:
                print("❌ Executable not found after build")
                return False
    elif system == "Windows":
        executable_path = dist_dir / "PME_Calculator.exe"
        if executable_path.exists():
            print(f"✅ Windows executable created: {executable_path}")
        else:
            print("❌ Windows executable not found after build")
            return False
    else:  # Linux
        executable_path = dist_dir / "PME_Calculator"
        if executable_path.exists():
            print(f"✅ Linux executable created: {executable_path}")
        else:
            print("❌ Linux executable not found after build")
            return False

    return True


def create_distribution():
    """Create a distribution package."""
    print("\n📦 Creating distribution package...")

    # Create dist directory at project root
    project_root = Path.cwd()
    final_dist = project_root / "dist"

    if final_dist.exists():
        shutil.rmtree(final_dist)
    final_dist.mkdir()

    # Copy executable/app
    backend_dist = Path("backend/dist")
    system = platform.system()

    if system == "Darwin":  # macOS
        app_bundle = backend_dist / "PME Calculator.app"
        standalone_exe = backend_dist / "PME_Calculator"

        if app_bundle.exists():
            print("📱 Copying macOS app bundle...")
            shutil.copytree(app_bundle, final_dist / "PME Calculator.app")
            executable_name = "PME Calculator.app"
        elif standalone_exe.exists():
            print("📱 Copying macOS executable...")
            shutil.copy2(standalone_exe, final_dist / "PME_Calculator")
            executable_name = "PME_Calculator"
        else:
            print("❌ No executable found to distribute")
            return False
    elif system == "Windows":
        exe_file = backend_dist / "PME_Calculator.exe"
        if exe_file.exists():
            print("💻 Copying Windows executable...")
            shutil.copy2(exe_file, final_dist / "PME_Calculator.exe")
            executable_name = "PME_Calculator.exe"
        else:
            print("❌ Windows executable not found")
            return False
    else:  # Linux
        exe_file = backend_dist / "PME_Calculator"
        if exe_file.exists():
            print("🐧 Copying Linux executable...")
            shutil.copy2(exe_file, final_dist / "PME_Calculator")
            # Make executable on Linux
            os.chmod(final_dist / "PME_Calculator", 0o755)
            executable_name = "PME_Calculator"
        else:
            print("❌ Linux executable not found")
            return False

    # Copy README and documentation
    readme_file = project_root / "README.md"
    if readme_file.exists():
        shutil.copy2(readme_file, final_dist / "README.md")

    # Create installation instructions
    install_instructions = final_dist / "INSTALLATION.txt"
    with open(install_instructions, "w") as f:
        f.write(
            f"""PME Calculator - Installation Instructions

QUICK START:
{'1. Double-click "PME Calculator.app" to launch the application' if system == 'Darwin' and
        app_bundle.exists() else f'1. Double-click "{executable_name}" to launch the application'}

SYSTEM REQUIREMENTS:
- {system} operating system
- No additional software installation required

USAGE:
1. Launch the application
2. Upload your fund data file (CSV or Excel)
3. Optionally upload benchmark index data
4. View analysis results and interactive charts

SUPPORT:
- Check README.md for detailed documentation
- Ensure your data files follow the expected format

Version: 1.0.0
Built on: {platform.platform()}
"""
        )

    print(f"✅ Distribution package created in: {final_dist}")
    print(f"🎉 Ready to distribute: {executable_name}")

    return True


def main():
    """Main build process."""
    print("🚀 PME Calculator Build Process")
    print("=" * 50)

    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    print(f"📁 Working directory: {project_root}")

    # Check dependencies
    if not check_dependencies():
        print("❌ Build failed: Missing dependencies")
        sys.exit(1)

    # Build frontend
    if not build_frontend():
        print("❌ Build failed: Frontend build error")
        sys.exit(1)

    # Build executable
    if not build_executable():
        print("❌ Build failed: PyInstaller error")
        sys.exit(1)

    # Create distribution
    if not create_distribution():
        print("❌ Build failed: Distribution creation error")
        sys.exit(1)

    print("\n🎉 BUILD SUCCESSFUL!")
    print("=" * 50)
    print("Your PME Calculator is ready for distribution!")
    print(f"📦 Find the distributable files in: {project_root / 'dist'}")

    system = platform.system()
    if system == "Darwin":
        print("🍎 macOS: Double-click the .app bundle to run")
    elif system == "Windows":
        print("💻 Windows: Double-click the .exe file to run")
    else:
        print("🐧 Linux: Run the executable from terminal or file manager")


if __name__ == "__main__":
    main()
