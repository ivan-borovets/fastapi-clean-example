#!/bin/bash
# The script is called from Makefile
DOCKER_COMPOSE_COMMAND=$1
DOCKER_COMPOSE_FILE=$2

services=$($DOCKER_COMPOSE_COMMAND -f "$DOCKER_COMPOSE_FILE" ps --services)
if [ -z "$services" ]; then
    echo "No running services found."
    exit 1
fi

echo "Running services:"
echo "$services" | awk '{print NR ") " $0}'
echo ""
read -rp "Enter the number of the service to view logs (or press Enter for all): " choice

if [ -z "$choice" ]; then
    $DOCKER_COMPOSE_COMMAND -f "$DOCKER_COMPOSE_FILE" logs -f
else
    service_count=$(echo "$services" | wc -l)
    if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt "$service_count" ]; then
        echo "Invalid choice. Please enter a number between 1 and $service_count."
        exit 1
    fi
    selected_service=$(echo "$services" | sed -n "${choice}p")
    echo "Viewing logs for service: $selected_service"
    $DOCKER_COMPOSE_COMMAND -f "$DOCKER_COMPOSE_FILE" logs -f "$selected_service"
fi
