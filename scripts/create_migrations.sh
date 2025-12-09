#!/bin/bash

# Script to create initial migrations for all apps

set -e

echo "🔄 Creating migrations for all apps..."

# Make sure containers are running
docker-compose up -d db redis web

echo "⏳ Waiting for services..."
sleep 5

echo "📝 Creating migrations for accounts app..."
docker-compose exec -T web python manage.py makemigrations accounts

echo "📝 Creating migrations for courses app..."
docker-compose exec -T web python manage.py makemigrations courses

echo "📝 Creating migrations for exercises app..."
docker-compose exec -T web python manage.py makemigrations exercises

echo "📝 Creating migrations for sandbox app..."
docker-compose exec -T web python manage.py makemigrations sandbox

echo "📝 Creating migrations for progress app..."
docker-compose exec -T web python manage.py makemigrations progress

echo "✅ All migrations created!"
echo ""
echo "Next: Run ./scripts/start.sh to apply migrations"
