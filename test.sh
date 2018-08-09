#!/bin/bash
set -e
source venv/bin/activate
pytest --show-capture=all -s -vvv --cov=b3/
