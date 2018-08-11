import os
from os.path import join
SRC_DIR = os.path.realpath(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)
ORG_DIR = join(PROJECT_DIR, "project")
DEFAULT_PROJECT_FILE = 'default'

#
# terraform
#

INSTANCE_DIR = join(ORG_DIR, 'instances') # ./project/instances

#
# testing
#

TEST_DIR = join(SRC_DIR, 'tests')
TEST_FIXTURE_DIR = join(TEST_DIR, 'fixtures')

#
# ansible
#

# a simple list of all known instances, grouped in different ways 
INVENTORY_FILE = join(PROJECT_DIR, 'inventory')
