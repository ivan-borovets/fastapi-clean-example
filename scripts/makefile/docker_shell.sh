#!/bin/bash
# The script is called from Makefile
containers=$(docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}" | awk 'NR>1')
if [ -z "$containers" ]; then
    echo "No running containers found."
    exit 1
fi

echo "Running containers:"
echo "$containers" | awk '{print NR ") " $0}'
echo ""
read -rp "Enter the number of the container to access: " choice
container_count=$(echo "$containers" | wc -l)
if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt "$container_count" ]; then
    echo "Invalid choice. Please enter a number between 1 and $container_count."
    exit 1
fi
selected_container=$(echo "$containers" | sed -n "${choice}p" | awk '{print $1}')
echo "Accessing shell in container: $selected_container"
docker exec -it "$selected_container" sh
