#!/bin/bash
set -e
source venv/bin/activate
pyflakes tasks/ b3/

# E1101=no-member, temporary while python2 is still supported
# E1129=Not Context Manager, fabric issue
pylint -E tasks/ b3/ \
    --disable=E1129
