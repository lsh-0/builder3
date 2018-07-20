#!/bin/bash
set -e
source venv/bin/activate
pytest -vvv --cov=b3/
