#!/bin/bash

# Djarvis Reset Script - WARNING: This will delete all data!

set -e

echo "⚠️  WARNING: This will delete all data!"
read -p "Are you sure you want to reset? (yes/no): " -r
echo

if [[ ! $REPLY =~ ^yes$ ]]; then
    echo "Reset cancelled"
    exit 1
fi

echo "🗑️ Stopping containers..."
docker-compose down -v

echo "🧹 Cleaning up..."
rm -rf backend/staticfiles/*
rm -rf backend/media/*

echo "🔄 Rebuilding..."
docker-compose build

echo "🚀 Starting fresh..."
./scripts/start.sh

echo ""
echo "✅ Reset complete!"
echo "Don't forget to:"
echo "1. Create superuser: docker-compose exec web python manage.py createsuperuser"
echo "2. Load demo data: docker-compose exec web python manage.py loaddata fixtures/demo_data.json"
