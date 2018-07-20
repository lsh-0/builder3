#!/bin/bash
set -e
source venv/bin/activate
pyflakes tasks.py b3/
pylint -E tasks.py b3/
