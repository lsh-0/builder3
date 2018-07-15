import os
from os.path import join
SRC_DIR = os.path.realpath(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)
ORG_DIR = join(PROJECT_DIR, "projects")
INSTANCE_DIR = join(PROJECT_DIR, 'instances')
DEFAULT_PROJECT_FILE = 'default'

# testing
TEST_DIR = join(SRC_DIR, 'tests')
TEST_FIXTURE_DIR = join(TEST_DIR, 'fixtures')
