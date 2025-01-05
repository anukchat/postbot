#!/bin/bash

# Function to display usage
show_usage() {
    echo "Usage: $0 [up|down|logs|rebuild]"
    exit 1
}

case "$1" in
    up)
        docker-compose up -d
        ;;
    down)
        docker-compose down
        ;;
    logs)
        docker-compose logs -f
        ;;
    rebuild)
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    *)
        show_usage
        ;;
esac
