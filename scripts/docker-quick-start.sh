#!/bin/bash
# Quick Docker Start Script for Secure Academic Browser

echo "🚀 Starting Secure Academic Browser with Docker..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Start services
echo "📦 Starting Docker services..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Services started!"
echo ""
echo "📋 Next Steps:"
echo "   1. Wait 30-60 seconds for database initialization"
echo "   2. Run: python setup_databases.py"
echo "   3. Run: python populate_sample_data.py"
echo "   4. Run: python main.py"
echo ""
echo "🌐 Access Points:"
echo "   - Dashboard: http://localhost:3000"
echo "   - API: http://localhost:5000"
echo "   - Database: localhost:3306"
echo ""
echo "📝 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"

