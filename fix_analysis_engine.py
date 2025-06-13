#!/usr/bin/env python3
"""
Quick fix for analysis_engine import issues.
"""

import os
from pathlib import Path


def fix_analysis_engine():
    """Fix the analysis_engine.py import issue."""
    print("🔧 Fixing analysis_engine.py import issue...")

    backend_dir = Path("pme_calculator/backend")
    analysis_engine_file = backend_dir / "analysis_engine.py"

    if not analysis_engine_file.exists():
        print("❌ analysis_engine.py not found")
        return False

    # Read current content
    content = analysis_engine_file.read_text()

    # Fix the relative import
    fixed_content = content.replace(
        "from .analysis_engine_legacy import *", "from analysis_engine_legacy import *"
    )

    # Write back
    analysis_engine_file.write_text(fixed_content)
    print("✅ Fixed relative import in analysis_engine.py")

    # Check if legacy file has the class
    legacy_file = backend_dir / "analysis_engine_legacy.py"
    if legacy_file.exists():
        legacy_content = legacy_file.read_text()
        if "class PMEAnalysisEngine" in legacy_content:
            print("✅ PMEAnalysisEngine class found in legacy file")
            return True
        else:
            print("⚠️  PMEAnalysisEngine class missing from legacy file")
            return False
    else:
        print("❌ analysis_engine_legacy.py not found")
        return False


def test_import():
    """Test the import after fix."""
    print("🧪 Testing import after fix...")

    backend_dir = Path("pme_calculator/backend")
    original_dir = os.getcwd()

    try:
        os.chdir(backend_dir)

        from analysis_engine import PMEAnalysisEngine

        print("✅ Import successful!")

        # Test instantiation
        engine = PMEAnalysisEngine()
        print("✅ Instantiation successful!")

        return True

    except Exception as e:
        print(f"❌ Import still failing: {e}")
        return False
    finally:
        os.chdir(original_dir)


def main():
    """Main fix function."""
    print("🔧 Analysis Engine Quick Fix")
    print("=" * 30)

    if fix_analysis_engine():
        if test_import():
            print("\n🎉 Analysis engine fixed successfully!")
            return True

    print("\n❌ Fix unsuccessful. Manual intervention needed.")
    return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
