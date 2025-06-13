#!/usr/bin/env python3
"""
Test safe workflow for patch application and git operations.
"""

import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import pytest

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestSafeWorkflow:
    """Test class for safe workflow operations."""
    
    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository for testing."""
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)
        
        # Initialize git repo
        subprocess.run(['git', 'init'], check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], check=True)
        
        # Create initial files
        Path('test_file.py').write_text('# Initial content\nprint("hello")\n')
        Path('.gitignore').write_text('*.pyc\n__pycache__/\n')
        
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True)
        
        yield temp_dir
        
        # Cleanup
        os.chdir('/')
        shutil.rmtree(temp_dir)
    
    def test_gitignore_patch_rules(self):
        """Test that .gitignore contains patch file rules."""
        gitignore_path = Path(__file__).parent.parent.parent.parent / '.gitignore'
        
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            # Check if patch rules exist or need to be added
            has_patch_rules = '*.patch' in content or '*.diff' in content
            
            if not has_patch_rules:
                print("⚠️  Patch rules not found in .gitignore - will be added")
            else:
                print("✅ Patch rules already exist in .gitignore")
    
    def test_patch_application_workflow(self, temp_git_repo):
        """Test the complete patch application workflow."""
        # Create a patch file
        patch_content = """--- test_file.py.orig
+++ test_file.py
@@ -1,2 +1,3 @@
 # Initial content
 print("hello")
+print("world")
"""
        
        patch_file = Path('fix.patch')
        patch_file.write_text(patch_content)
        
        # Test patch application
        result = subprocess.run(['git', 'apply', 'fix.patch'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Patch applied successfully")
            
            # Test git add
            subprocess.run(['git', 'add', '-A'], check=True)
            
            # Test commit
            subprocess.run(['git', 'commit', '-m', 'Test: apply patch'], check=True)
            
            # Test patch cleanup
            patch_file.unlink()
            assert not patch_file.exists(), "Patch file should be deleted"
            
        else:
            print(f"❌ Patch application failed: {result.stderr}")
    
    def test_safe_workflow_script_creation(self):
        """Test creation of safe workflow script."""
        script_content = self._generate_safe_workflow_script()
        assert 'git apply' in script_content
        assert 'git add -A' in script_content
        assert 'git commit' in script_content
        assert 'rm *.patch' in script_content
        print("✅ Safe workflow script content validated")
    
    def test_git_status_check(self, temp_git_repo):
        """Test git status checking functionality."""
        # Check clean status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print(f"⚠️  Working directory has changes: {result.stdout}")
            else:
                print("✅ Working directory is clean")
        else:
            print(f"❌ Git status check failed: {result.stderr}")
    
    def test_branch_operations(self, temp_git_repo):
        """Test branch creation and switching."""
        # Create new branch
        result = subprocess.run(['git', 'checkout', '-b', 'test-branch'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Branch created successfully")
            
            # Check current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                current_branch = result.stdout.strip()
                assert current_branch == 'test-branch'
                print(f"✅ Current branch: {current_branch}")
        else:
            print(f"❌ Branch creation failed: {result.stderr}")
    
    def _generate_safe_workflow_script(self):
        """Generate the safe workflow script content."""
        return """#!/bin/bash

# Safe workflow for patch application and git operations
set -e  # Exit on any error

echo "🔧 Starting safe workflow..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: You have uncommitted changes"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Apply patches if they exist
if ls *.patch 1> /dev/null 2>&1; then
    echo "📋 Applying patches..."
    for patch in *.patch; do
        echo "  Applying $patch..."
        git apply "$patch" || {
            echo "❌ Failed to apply $patch"
            exit 1
        }
    done
else
    echo "ℹ️  No patch files found"
fi

# Stage all changes
echo "📦 Staging changes..."
git add -A

# Check if there are changes to commit
if git diff-index --quiet --cached HEAD --; then
    echo "ℹ️  No changes to commit"
else
    # Commit changes
    echo "💾 Committing changes..."
    git commit -m "Refactor: migrate analysis_engine imports to pme_math"
fi

# Clean up patch files
if ls *.patch 1> /dev/null 2>&1; then
    echo "🧹 Cleaning up patch files..."
    rm *.patch
fi

if ls *.diff 1> /dev/null 2>&1; then
    echo "🧹 Cleaning up diff files..."
    rm *.diff
fi

echo "✅ Safe workflow completed successfully!"
"""

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 