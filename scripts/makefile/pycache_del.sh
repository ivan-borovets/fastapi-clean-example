#!/bin/bash
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +; \
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
