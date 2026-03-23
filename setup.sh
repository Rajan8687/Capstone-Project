#!/bin/bash

echo "🚀 InsightWrite Project Manager"
echo "================================"
echo ""
echo "Available commands:"
echo "  ./setup.sh start     - Start the project (build + run)"
echo "  ./setup.sh stop      - Stop all containers"
echo "  ./setup.sh restart   - Restart the project"
echo "  ./setup.sh build     - Rebuild containers"
echo "  ./setup.sh logs      - View logs"
echo "  ./setup.sh migrate   - Run database migrations"
echo "  ./setup.sh shell     - Open Django shell"
echo "  ./setup.sh clean     - Remove all containers and volumes"
echo "  ./setup.sh status    - Check container status"
echo ""

case "$1" in
    start)
        echo "🚀 Starting InsightWrite..."
        docker compose up --build -d
        echo ""
        echo "✅ Project started!"
        echo "🌐 Web App: http://localhost:8000"
        echo "🔧 Admin: http://localhost:8000/admin"
        ;;
    stop)
        echo "🛑 Stopping InsightWrite..."
        docker compose down
        echo "✅ Project stopped!"
        ;;
    restart)
        echo "🔄 Restarting InsightWrite..."
        docker compose down
        docker compose up --build -d
        echo ""
        echo "✅ Project restarted!"
        echo "🌐 Web App: http://localhost:8000"
        ;;
    build)
        echo "🔨 Building containers..."
        docker compose up --build -d
        echo "✅ Build complete!"
        ;;
    logs)
        echo "📋 Showing logs..."
        docker compose logs -f
        ;;
    migrate)
        echo "🗄️ Running migrations..."
        docker compose exec web python manage.py migrate
        echo "✅ Migrations complete!"
        ;;
    shell)
        echo "🐚 Opening Django shell..."
        docker compose exec web python manage.py shell
        ;;
    clean)
        echo "Cleaning up..."
        docker compose down -v
        docker system prune -f
        echo "Cleanup complete!"
        ;;
    status)
        echo "📊 Container status:"
        docker compose ps
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        echo "Usage: ./setup.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start, stop, restart, build, logs, migrate, shell, clean, status"
        ;;
esac
