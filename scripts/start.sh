#!/bin/bash

# Djarvis Start Script

set -e

echo "🎓 Starting Djarvis..."
echo ""

# Check if frontend is built
if [ ! -d "frontend/dist" ]; then
    echo "⚠️  Frontend not built. Building now..."
    cd frontend
    npm install
    npm run build
    cd ..
    echo "✅ Frontend built"
fi

# Start containers
echo "🚀 Starting Docker containers..."
docker-compose up -d db redis

echo ""
echo "⏳ Waiting for database to be ready..."
sleep 10

# Start web services
docker-compose up -d web celery_worker celery_beat

echo ""
echo "⏳ Waiting for web service to be ready..."
sleep 5

# Run migrations
echo "🔄 Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Collect static files
echo "📚 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Start nginx
docker-compose up -d nginx

echo ""
echo "✅ Djarvis is running!"
echo ""
echo "Services:"
echo "  Frontend:  http://localhost"
echo "  API:       http://localhost/api/"
echo "  Admin:     http://localhost/admin/"
echo "  API Docs:  http://localhost/api/docs/"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop:             docker-compose down"
echo "  Restart:          docker-compose restart"
echo ""
echo "Next steps:"
echo "  1. Create superuser: docker-compose exec web python manage.py createsuperuser"
echo "  2. Load demo data:   docker-compose exec web python manage.py loaddata fixtures/demo_data.json"
