#!/usr/bin/env python3
"""
Quick test to validate UploadFileMeta imports before and after fixes.
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def test_current_imports():
    """Test current import state."""
    print("🔍 Testing current import state...")

    # Test 1: Import from models package
    try:
        from models import UploadFileMeta

        print("✅ models package import: SUCCESS")
        print(f"   Table name: {UploadFileMeta.__tablename__}")
    except Exception as e:
        print(f"❌ models package import: FAILED - {e}")

    # Test 2: Direct import from models.upload_meta
    try:
        from models.upload_meta import UploadFileMeta as DirectImport

        print("✅ models.upload_meta import: SUCCESS")
        print(f"   Table name: {DirectImport.__tablename__}")
    except Exception as e:
        print(f"❌ models.upload_meta import: FAILED - {e}")

    # Test 3: Database module import (should work after fix)
    try:
        import database

        if hasattr(database, "UploadFileMeta") and database.UploadFileMeta is not None:
            if hasattr(database.UploadFileMeta, "__tablename__"):
                print("✅ database.py import: SUCCESS (real model)")
                print(f"   Table name: {database.UploadFileMeta.__tablename__}")
            else:
                print("⚠️  database.py import: FALLBACK (placeholder class)")
        else:
            print("❌ database.py import: FAILED")
    except Exception as e:
        print(f"❌ database.py import: FAILED - {e}")


if __name__ == "__main__":
    test_current_imports()
