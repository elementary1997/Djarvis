#!/bin/bash

# Djarvis Setup Script
# This script sets up the development environment

set -e

echo "🎓 Djarvis Setup Script"
echo "========================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "🔧 Creating .env file from template..."
    cp backend/.env.example backend/.env
    
    # Generate secret key
    SECRET_KEY=$(python3 -c "import random, string; print(''.join(random.SystemRandom().choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(50)))" 2>/dev/null || echo "change-this-secret-key-in-production-$(date +%s)")
    
    # Update .env with generated secret key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-secret-key-change-this-in-production/$SECRET_KEY/" backend/.env
    else
        sed -i "s/your-secret-key-change-this-in-production/$SECRET_KEY/" backend/.env
    fi
    
    echo "✅ .env file created with generated secret key"
else
    echo "ℹ️  .env file already exists"
fi

# Build frontend first
echo ""
echo "📦 Building frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi
echo "Building React app..."
npm run build
cd ..

echo "✅ Frontend built successfully"

# Build backend containers
echo ""
echo "🛠️ Building Docker containers..."
docker-compose build web celery_worker celery_beat

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the application: ./scripts/start.sh"
echo "2. Create a superuser: docker-compose exec web python manage.py createsuperuser"
echo "3. Load demo data: docker-compose exec web python manage.py loaddata fixtures/demo_data.json"
echo "4. Access the application at http://localhost"
