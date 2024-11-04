#!/bin/bash
# The script is called from Makefile
echo "Warning: This will remove all unused containers, networks, images, and volumes."
echo "Are you sure you want to continue? [y/N]"
read -r response
if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    docker system prune -a --volumes
else
    echo "Operation cancelled."
fi
