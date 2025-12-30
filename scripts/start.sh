#!/bin/bash
# EduBrowser Docker Startup Script
# Usage: ./start.sh [command]

set -e

COMMAND=${1:-up}
COMPOSE_FILE="docker-compose.yml"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      EduBrowser Docker Manager    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════╝${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file${NC}"
        echo -e "${YELLOW}  Please review and edit .env if needed${NC}"
    fi
fi

case "$COMMAND" in
    up|start)
        echo -e "${BLUE}🚀 Starting EduBrowser services...${NC}"
        docker-compose up -d
        echo -e "${GREEN}✓ Services started${NC}"
        sleep 2
        docker-compose ps
        echo ""
        echo -e "${GREEN}📍 Access points:${NC}"
        echo -e "   React Dashboard: ${BLUE}http://localhost:3000${NC}"
        echo -e "   API Server:      ${BLUE}http://localhost:5000${NC}"
        echo -e "   Database:        ${BLUE}localhost:3306${NC}"
        ;;
    
    down|stop)
        echo -e "${BLUE}⏹️  Stopping EduBrowser services...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ Services stopped${NC}"
        ;;
    
    restart)
        echo -e "${BLUE}🔄 Restarting EduBrowser services...${NC}"
        docker-compose restart
        echo -e "${GREEN}✓ Services restarted${NC}"
        ;;
    
    logs)
        SERVICE=${2:-app}
        echo -e "${BLUE}📋 Showing logs for $SERVICE...${NC}"
        docker-compose logs -f $SERVICE
        ;;
    
    status|ps)
        echo -e "${BLUE}📊 Service Status:${NC}"
        docker-compose ps
        ;;
    
    rebuild)
        echo -e "${BLUE}🔨 Rebuilding containers...${NC}"
        docker-compose build
        echo -e "${BLUE}🚀 Starting services...${NC}"
        docker-compose up -d
        echo -e "${GREEN}✓ Rebuilt and started${NC}"
        ;;
    
    clean)
        echo -e "${YELLOW}⚠️  This will remove all containers and volumes${NC}"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}🧹 Cleaning up...${NC}"
            docker-compose down -v
            echo -e "${GREEN}✓ Cleaned up${NC}"
        else
            echo -e "${YELLOW}Cancelled${NC}"
        fi
        ;;
    
    health)
        echo -e "${BLUE}🏥 Checking service health...${NC}"
        echo ""
        echo -e "${BLUE}API Server:${NC}"
        curl -s http://localhost:5000/health | jq . || echo "Not responding"
        echo ""
        echo -e "${BLUE}Database:${NC}"
        docker-compose exec db mysqladmin ping -u root -p$(grep DB_PASSWORD .env | cut -d= -f2) || echo "Not responding"
        ;;
    
    help)
        echo -e "${GREEN}Available commands:${NC}"
        echo ""
        echo -e "  ${BLUE}./start.sh up${NC}        - Start services"
        echo -e "  ${BLUE}./start.sh down${NC}      - Stop services"
        echo -e "  ${BLUE}./start.sh restart${NC}   - Restart services"
        echo -e "  ${BLUE}./start.sh rebuild${NC}   - Rebuild containers"
        echo -e "  ${BLUE}./start.sh logs${NC} [service] - View logs"
        echo -e "  ${BLUE}./start.sh status${NC}    - Show service status"
        echo -e "  ${BLUE}./start.sh health${NC}    - Check service health"
        echo -e "  ${BLUE}./start.sh clean${NC}     - Remove all containers and volumes"
        echo -e "  ${BLUE}./start.sh help${NC}      - Show this help message"
        echo ""
        echo -e "${GREEN}Examples:${NC}"
        echo -e "  ${BLUE}./start.sh${NC}           - Start all services"
        echo -e "  ${BLUE}./start.sh logs app${NC}  - Show API server logs"
        echo -e "  ${BLUE}./start.sh logs dashboard${NC} - Show dashboard logs"
        ;;
    
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo "Run './start.sh help' for available commands"
        exit 1
        ;;
esac
