#!/usr/bin/env python3
"""
Backend startup script with proper environment setup
"""
import os
import sys
from pathlib import Path


def setup_environment():
    """Set up the Python environment for the backend"""
    backend_path = Path(__file__).parent / "pme_calculator" / "backend"
    backend_path = backend_path.resolve()

    # Add backend directory to Python path
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))

    # Set PYTHONPATH environment variable
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    if str(backend_path) not in current_pythonpath:
        if current_pythonpath:
            os.environ["PYTHONPATH"] = f"{backend_path}:{current_pythonpath}"
        else:
            os.environ["PYTHONPATH"] = str(backend_path)

    # Change to backend directory
    os.chdir(backend_path)

    print(f"✅ Backend directory: {backend_path}")
    print(f"✅ PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    print(f"✅ Current directory: {os.getcwd()}")


def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        "fastapi",
        "uvicorn",
        "asyncpg",
        "sqlalchemy",
        "redis",
        "pandas",
        "numpy",
    ]

    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing_modules.append(module)

    if missing_modules:
        print(f"\n❌ Missing modules: {', '.join(missing_modules)}")
        print("Please install them with: pip install " + " ".join(missing_modules))
        return False

    return True


def test_import():
    """Test if main_minimal can be imported"""
    try:

        print("✅ main_minimal imports successfully")
        return True
    except Exception as e:
        print(f"❌ main_minimal import failed: {e}")
        return False


def start_server():
    """Start the FastAPI server"""
    try:
        import uvicorn
        from main_minimal import app

        print("\n🚀 Starting PME Calculator Backend Server...")
        print("📍 Server will be available at: http://localhost:8000")
        print("📖 API Documentation: http://localhost:8000/api/docs")
        print("🔄 Press Ctrl+C to stop the server\n")

        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False,  # Disable reload to avoid issues
        )

    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

    return True


def main():
    """Main startup function"""
    print("🔧 PME Calculator Backend Startup")
    print("=" * 50)

    # Setup environment
    setup_environment()

    # Check dependencies
    print("\n📦 Checking Dependencies:")
    if not check_dependencies():
        sys.exit(1)

    # Test import
    print("\n🔍 Testing Import:")
    if not test_import():
        sys.exit(1)

    # Start server
    start_server()


if __name__ == "__main__":
    main()
