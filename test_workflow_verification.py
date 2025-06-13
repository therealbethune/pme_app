#!/usr/bin/env python3
"""
Test script to verify the safe workflow implementation.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path

def test_safe_workflow():
    """Test the safe workflow script."""
    print("🧪 Testing safe workflow implementation...")
    
    # Check if safe_workflow.sh exists and is executable
    workflow_script = Path("safe_workflow.sh")
    
    if not workflow_script.exists():
        print("❌ safe_workflow.sh not found")
        return False
    
    # Make it executable
    os.chmod(workflow_script, 0o755)
    print("✅ Workflow script found and made executable")
    
    # Check .gitignore rules
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if "*.patch" in content and "*.diff" in content:
            print("✅ .gitignore contains patch file rules")
        else:
            print("⚠️  .gitignore missing patch file rules")
    else:
        print("⚠️  .gitignore file not found")
    
    # Test script syntax (dry run)
    try:
        result = subprocess.run(['bash', '-n', str(workflow_script)], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Workflow script syntax is valid")
        else:
            print(f"❌ Script syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing script: {e}")
        return False
    
    print("🎉 Safe workflow verification completed!")
    return True

if __name__ == "__main__":
    success = test_safe_workflow()
    exit(0 if success else 1) 