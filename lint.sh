#!/bin/bash
set -e
source venv/bin/activate
pyflakes tasks/ b3/

# E1101=no-member, temporary while python2 is still supported
pylint -E tasks/ b3/ \
    --disable=E1101
