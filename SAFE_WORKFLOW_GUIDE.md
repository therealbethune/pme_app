# Safe Workflow Guide

This guide explains how to safely apply patches and manage git operations using the provided workflow tools.

## Overview

The safe workflow provides a systematic approach to:
1. Apply patch files safely
2. Stage and commit changes
3. Clean up temporary files
4. Update .gitignore rules
5. Push changes to remote repository

## Files

- `safe_workflow.sh` - Main workflow script
- `test_workflow_verification.py` - Verification script
- `SAFE_WORKFLOW_GUIDE.md` - This guide

## Usage

### Basic Usage

```bash
# Make the script executable (first time only)
chmod +x safe_workflow.sh

# Run the workflow
./safe_workflow.sh
```

### What the Script Does

1. **Repository Check**: Verifies you're in a git repository
2. **Status Check**: Warns about uncommitted changes
3. **Gitignore Update**: Adds patch file rules to .gitignore
4. **Patch Application**: Applies any .patch or .diff files found
5. **Staging**: Stages all changes with `git add -A`
6. **Commit**: Commits with a standard message
7. **Cleanup**: Removes patch and diff files
8. **Push Option**: Offers to push changes to remote

### Manual Steps (Alternative)

If you prefer manual control:

```bash
# 1. Apply patches
git apply fix.patch

# 2. Stage changes
git add -A

# 3. Commit
git commit -m "Refactor: migrate analysis_engine imports to pme_math"

# 4. Clean up
rm fix.patch

# 5. Push
git push origin your-branch
```

### Safety Features

- **Pre-flight checks**: Validates git repository and status
- **Patch validation**: Tests patches before applying
- **User confirmation**: Asks before proceeding with uncommitted changes
- **Error handling**: Exits on any error with clear messages
- **Cleanup**: Automatically removes temporary files

### Error Handling

The script will stop and show an error if:
- Not in a git repository
- Patch application fails
- Git operations fail

### Gitignore Rules

The script automatically adds these rules to .gitignore:

```gitignore
# Ignore patch/diff scratch files
*.patch
*.diff
```

## Testing

Run the verification script to test the workflow:

```bash
python3 test_workflow_verification.py
```

## Examples

### Example 1: Simple Patch Application

```bash
# You have a fix.patch file
ls *.patch
# fix.patch

# Run the workflow
./safe_workflow.sh
# 🔧 Starting safe workflow for patch application...
# ✅ Git repository detected
# ✅ Working directory is clean
# ✅ Patch file rules already exist in .gitignore
# 📋 Found patch files, applying...
# ✅ Applied 1 patch file(s)
# 💾 Committing changes...
# ✅ Changes committed successfully
# 🧹 Cleaning up patch and diff files...
# ✅ Cleaned up patch files
# 🎉 Safe workflow completed successfully!
```

### Example 2: Multiple Patches

```bash
# Multiple patch files
ls *.patch
# feature.patch  bugfix.patch

./safe_workflow.sh
# Applies both patches, commits, and cleans up
```

### Example 3: With Push

```bash
./safe_workflow.sh
# ... (normal workflow)
# 🚀 Ready to push changes?
#    Current branch: feature-branch
#    Remote: origin/feature-branch
# 
# Push to origin/feature-branch? (y/N): y
# 📤 Pushing to origin/feature-branch...
# ✅ Successfully pushed to origin/feature-branch
```

## Best Practices

1. **Review patches first**: Always review patch content before applying
2. **Clean working directory**: Commit or stash changes before running
3. **Test after applying**: Run tests after patch application
4. **Meaningful commits**: The script uses a standard message, but you can modify it
5. **Branch management**: Work on feature branches, not main/master

## Troubleshooting

### Common Issues

**"Not in a git repository"**
- Solution: Run from within a git repository

**"Failed to apply patch"**
- Solution: Check patch format and target files
- The script will show specific error details

**"You have uncommitted changes"**
- Solution: Commit or stash changes first, or choose to continue

**Push fails**
- Solution: Set up remote branch with `git push -u origin branch-name`

### Getting Help

The script provides detailed error messages and suggestions for resolution.

## Advanced Usage

### Custom Commit Messages

Edit the script to change the commit message:

```bash
# Find this line in safe_workflow.sh
local commit_msg="Refactor: migrate analysis_engine imports to pme_math"

# Change to your preferred message
local commit_msg="Your custom commit message"
```

### Skip Push Prompt

To always skip the push prompt, comment out the `offer_push` call in the main function.

### Dry Run Mode

For testing, you can add a dry-run mode by modifying the script to echo commands instead of executing them. 