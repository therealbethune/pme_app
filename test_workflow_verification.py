#!/usr/bin/env python3
"""
Test script to verify the safe workflow implementation.
"""

import os
import subprocess
from pathlib import Path

import structlog

logger = structlog.get_logger()


def test_safe_workflow():
    """Test the safe workflow script."""
    logger.debug("🧪 Testing safe workflow implementation...")

    # Check if safe_workflow.sh exists and is executable
    workflow_script = Path("safe_workflow.sh")

    if not workflow_script.exists():
        logger.debug("❌ safe_workflow.sh not found")
        return False

    # Make it executable
    os.chmod(workflow_script, 0o755)
    logger.debug("✅ Workflow script found and made executable")

    # Check .gitignore rules
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if "*.patch" in content and "*.diff" in content:
            logger.debug("✅ .gitignore contains patch file rules")
        else:
            logger.debug("⚠️  .gitignore missing patch file rules")
    else:
        logger.debug("⚠️  .gitignore file not found")

    # Test script syntax (dry run)
    try:
        result = subprocess.run(
            ["bash", "-n", str(workflow_script)], capture_output=True, text=True
        )
        if result.returncode == 0:
            logger.debug("✅ Workflow script syntax is valid")
        else:
            logger.debug(f"❌ Script syntax error: {result.stderr}")
            return False
    except Exception as e:
        logger.debug(f"❌ Error testing script: {e}")
        return False

    logger.debug("🎉 Safe workflow verification completed!")
    return True


if __name__ == "__main__":
    success = test_safe_workflow()
    exit(0 if success else 1)
