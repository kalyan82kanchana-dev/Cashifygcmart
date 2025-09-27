#!/bin/bash

echo "🔍 Checking deployment readiness for Railway..."

# Check backend
echo "📋 Checking backend..."
cd backend
if python3 -c "import server; print('✅ Backend imports successfully')"; then
    echo "✅ Backend: Ready for deployment"
else
    echo "❌ Backend: Import failed"
    exit 1
fi

# Check frontend build
echo "📋 Checking frontend build..."
cd ../frontend
if npm run build > /dev/null 2>&1; then
    echo "✅ Frontend: Build successful"
    if [ -d "build" ]; then
        echo "✅ Frontend: Build directory exists"
    else
        echo "❌ Frontend: Build directory missing"
        exit 1
    fi
else
    echo "❌ Frontend: Build failed"
    exit 1
fi

# Check Railway config
echo "📋 Checking Railway configuration..."
cd ..
if [ -f "railway.toml" ]; then
    echo "✅ Railway config: railway.toml exists"
else
    echo "❌ Railway config: railway.toml missing"
    exit 1
fi

if [ -f "nixpacks.toml" ]; then
    echo "✅ Nixpacks config: nixpacks.toml exists"
else
    echo "❌ Nixpacks config: nixpacks.toml missing"
    exit 1
fi

echo ""
echo "🎉 All checks passed! Your app is ready for Railway deployment."
echo ""
echo "📋 Next steps:"
echo "1. Push your code to GitHub"
echo "2. Connect your GitHub repo to Railway"
echo "3. Railway will auto-deploy your app"
echo ""
echo "🌐 Your app will be available at: https://your-app-name.railway.app"
