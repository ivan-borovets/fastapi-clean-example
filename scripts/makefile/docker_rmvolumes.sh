#!/bin/bash
# The script is called from Makefile
echo "Warning: This will remove all Docker volumes."
echo "Are you sure you want to continue? [y/N]"
read -r response
if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    docker volume rm "$(docker volume ls -q)"
else
    echo "Operation cancelled."
fi
