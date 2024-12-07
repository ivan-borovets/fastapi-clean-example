#!/bin/bash
# The script is called from docker-compose.yaml
python -m alembic upgrade head
python -m app.run
