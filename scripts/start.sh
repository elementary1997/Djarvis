#!/bin/bash

# Djarvis Start Script

set -e

echo "🎓 Starting Djarvis..."
echo ""

# Start containers
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run migrations
echo "🔄 Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Collect static files
echo "📚 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

echo ""
echo "✅ Djarvis is running!"
echo ""
echo "Services:"
echo "  Frontend:  http://localhost"
echo "  API:       http://localhost/api/"
echo "  Admin:     http://localhost/admin/"
echo "  API Docs:  http://localhost/api/docs/"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop:      docker-compose down"
