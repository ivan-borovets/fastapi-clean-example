#!/bin/bash
# The script is called from docker-compose.yaml
alembic upgrade head
python -m app.run
