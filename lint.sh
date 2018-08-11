#!/bin/bash
set -e
source venv/bin/activate
pyflakes tasks/ b3/
pylint -E tasks/ b3/
