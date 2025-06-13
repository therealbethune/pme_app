#!/bin/bash

# Safe workflow for patch application and git operations
set -e  # Exit on any error

echo "🔧 Starting safe workflow for patch application..."

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "❌ Error: Not in a git repository"
        echo "   Please run this script from within a git repository"
        exit 1
    fi
    echo "✅ Git repository detected"
}

# Function to check git status
check_git_status() {
    echo "📊 Checking git status..."
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "⚠️  Warning: You have uncommitted changes in your working directory"
        git status --short
        echo ""
        read -p "Continue anyway? This will stage and commit all changes (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Aborted by user"
            exit 1
        fi
    else
        echo "✅ Working directory is clean"
    fi
}

# Function to apply patches
apply_patches() {
    local patch_count=0
    
    echo "🔍 Looking for patch files..."
    
    # Apply .patch files
    if ls *.patch 1> /dev/null 2>&1; then
        echo "📋 Found patch files, applying..."
        for patch in *.patch; do
            echo "  📄 Applying $patch..."
            if git apply --check "$patch" 2>/dev/null; then
                git apply "$patch"
                echo "    ✅ Successfully applied $patch"
                ((patch_count++))
            else
                echo "    ❌ Failed to apply $patch"
                echo "    Checking what went wrong..."
                git apply "$patch" 2>&1 || true
                exit 1
            fi
        done
    fi
    
    # Apply .diff files
    if ls *.diff 1> /dev/null 2>&1; then
        echo "📋 Found diff files, applying..."
        for diff in *.diff; do
            echo "  📄 Applying $diff..."
            if git apply --check "$diff" 2>/dev/null; then
                git apply "$diff"
                echo "    ✅ Successfully applied $diff"
                ((patch_count++))
            else
                echo "    ❌ Failed to apply $diff"
                echo "    Checking what went wrong..."
                git apply "$diff" 2>&1 || true
                exit 1
            fi
        done
    fi
    
    if [ $patch_count -eq 0 ]; then
        echo "ℹ️  No patch or diff files found to apply"
    else
        echo "✅ Applied $patch_count patch file(s)"
    fi
    
    return $patch_count
}

# Function to stage and commit changes
commit_changes() {
    echo "📦 Staging all changes..."
    git add -A
    
    # Check if there are changes to commit
    if git diff-index --quiet --cached HEAD -- 2>/dev/null; then
        echo "ℹ️  No changes to commit"
        return 0
    else
        echo "💾 Committing changes..."
        
        # Get current branch name
        local branch_name=$(git branch --show-current 2>/dev/null || echo "unknown")
        
        # Create commit message
        local commit_msg="Refactor: migrate analysis_engine imports to pme_math"
        
        git commit -m "$commit_msg"
        echo "✅ Changes committed successfully"
        echo "   Branch: $branch_name"
        echo "   Message: $commit_msg"
        return 1
    fi
}

# Function to clean up patch files
cleanup_patches() {
    local cleaned=0
    
    echo "🧹 Cleaning up patch and diff files..."
    
    if ls *.patch 1> /dev/null 2>&1; then
        rm *.patch
        echo "  🗑️  Removed patch files"
        ((cleaned++))
    fi
    
    if ls *.diff 1> /dev/null 2>&1; then
        rm *.diff
        echo "  🗑️  Removed diff files"
        ((cleaned++))
    fi
    
    if [ $cleaned -eq 0 ]; then
        echo "ℹ️  No patch files to clean up"
    else
        echo "✅ Cleaned up patch files"
    fi
}

# Function to update .gitignore
update_gitignore() {
    local gitignore_file=".gitignore"
    
    if [ ! -f "$gitignore_file" ]; then
        echo "⚠️  No .gitignore file found, creating one..."
        touch "$gitignore_file"
    fi
    
    # Check if patch rules already exist
    if grep -q "*.patch" "$gitignore_file" && grep -q "*.diff" "$gitignore_file"; then
        echo "✅ Patch file rules already exist in .gitignore"
    else
        echo "📝 Adding patch file rules to .gitignore..."
        echo "" >> "$gitignore_file"
        echo "# Ignore patch/diff scratch files" >> "$gitignore_file"
        echo "*.patch" >> "$gitignore_file"
        echo "*.diff" >> "$gitignore_file"
        echo "✅ Updated .gitignore with patch file rules"
    fi
}

# Function to offer push option
offer_push() {
    echo ""
    echo "🚀 Ready to push changes?"
    
    # Get current branch
    local current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
    
    if [ "$current_branch" = "unknown" ]; then
        echo "⚠️  Could not determine current branch"
        return
    fi
    
    echo "   Current branch: $current_branch"
    echo "   Remote: origin/$current_branch"
    echo ""
    
    read -p "Push to origin/$current_branch? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Pushing to origin/$current_branch..."
        if git push origin "$current_branch"; then
            echo "✅ Successfully pushed to origin/$current_branch"
        else
            echo "❌ Failed to push. You may need to set up the remote branch:"
            echo "   git push -u origin $current_branch"
        fi
    else
        echo "ℹ️  Skipped push. You can push later with:"
        echo "   git push origin $current_branch"
    fi
}

# Main workflow
main() {
    echo "🔧 Safe Workflow for Patch Application and Git Operations"
    echo "========================================================"
    echo ""
    
    # Step 1: Check git repository
    check_git_repo
    
    # Step 2: Check git status
    check_git_status
    
    # Step 3: Update .gitignore
    update_gitignore
    
    # Step 4: Apply patches
    apply_patches
    local patches_applied=$?
    
    # Step 5: Commit changes
    commit_changes
    local changes_committed=$?
    
    # Step 6: Clean up patch files
    cleanup_patches
    
    # Step 7: Offer to push
    if [ $changes_committed -eq 1 ]; then
        offer_push
    fi
    
    echo ""
    echo "🎉 Safe workflow completed successfully!"
    
    if [ $patches_applied -gt 0 ] || [ $changes_committed -eq 1 ]; then
        echo ""
        echo "📋 Summary:"
        [ $patches_applied -gt 0 ] && echo "   • Applied $patches_applied patch file(s)"
        [ $changes_committed -eq 1 ] && echo "   • Committed changes"
        echo "   • Cleaned up temporary files"
        echo "   • Updated .gitignore"
    fi
}

# Run main function
main "$@" 