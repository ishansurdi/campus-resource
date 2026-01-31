#!/usr/bin/env bash
# Quick deployment check script

echo "🚀 CAMPUSPHERE Deployment Preparation Checklist"
echo "================================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python --version

# Check if requirements.txt exists
if [ -f "backend/requirements.txt" ]; then
    echo "✓ requirements.txt found"
else
    echo "✗ requirements.txt missing!"
    exit 1
fi

# Check if .env.example exists
if [ -f "backend/.env.example" ]; then
    echo "✓ .env.example found"
else
    echo "✗ .env.example missing!"
fi

# Check if .gitignore exists
if [ -f ".gitignore" ]; then
    echo "✓ .gitignore found"
else
    echo "✗ .gitignore missing!"
fi

# Check if build.sh exists
if [ -f "backend/build.sh" ]; then
    echo "✓ build.sh found"
    chmod +x backend/build.sh
else
    echo "✗ build.sh missing!"
fi

# Check git status
echo ""
echo "📋 Git Status:"
git status --short

echo ""
echo "✅ Deployment files check complete!"
echo ""
echo "Next steps:"
echo "1. Create .env file from .env.example"
echo "2. Configure database settings"
echo "3. Test locally: cd backend && python manage.py runserver"
echo "4. Push to GitHub: git push origin main"
echo "5. Follow DEPLOYMENT.md for Render setup"
