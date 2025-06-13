#!/bin/bash

echo "🧹 Starting frontend cleanup..."

# Remove node_modules directory
if [ -d "pme_calculator/frontend/node_modules" ]; then
    echo "🗑️  Removing node_modules directory..."
    rm -rf pme_calculator/frontend/node_modules
    echo "✅ node_modules removed"
else
    echo "✅ node_modules already clean"
fi

# Remove dist directory if it exists
if [ -d "pme_calculator/frontend/dist" ]; then
    echo "🗑️  Removing dist directory..."
    rm -rf pme_calculator/frontend/dist
    echo "✅ dist removed"
else
    echo "✅ dist directory already clean"
fi

# Check and update .gitignore
echo "🔍 Checking .gitignore entries..."
if [ -f ".gitignore" ]; then
    # Check for node_modules
    if ! grep -q "node_modules" .gitignore; then
        echo "📝 Adding node_modules to .gitignore"
        echo "" >> .gitignore
        echo "# Dependencies" >> .gitignore
        echo "node_modules/" >> .gitignore
    else
        echo "✅ node_modules already in .gitignore"
    fi
    
    # Check for dist
    if ! grep -q "dist" .gitignore; then
        echo "📝 Adding dist to .gitignore"
        echo "" >> .gitignore
        echo "# Build output" >> .gitignore
        echo "dist/" >> .gitignore
    else
        echo "✅ dist already in .gitignore"
    fi
else
    echo "⚠️  Creating .gitignore file"
    cat > .gitignore << EOF
# Dependencies
node_modules/

# Build output
dist/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
EOF
fi

echo "🎉 Frontend cleanup completed!" 