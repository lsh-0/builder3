#from . import utils
import os
from os.path import join
SRC_DIR = os.path.realpath(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)
ORG_DIR = join(PROJECT_DIR, "project")
DEFAULT_PROJECT_FILE = 'default'

BOOTSTRAP_USER = 'root' # actually, ubuntu, depending ...
BOOTSTRAP_PASS = 'root'
DEPLOY_USER = 'luke'

SCRIPTS_PATH = join(PROJECT_DIR, 'scripts')

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


#
'''


# sensible defaults used everywhere
GLOBAL_VARS = {
    'bootstrap-user': 'ubuntu', # ec2, droplets
    'deploy-user': 'luke', # bootstrap will create this user with sudo permissions
}

PER_INST_VARS = {}

# some resource types need
PER_TYPE_VARS = {
    'docker': {
        'bootstrap-user': 'docker',
    }
    'vagrant': {
        'bootstrap-user': 'vagrant'
    },
    'baremetal': {
        'bootstrap-user': 'root',
    }
}

def cfg(iid=None, resource=None):
    config = utils.deepcopy(GLOBAL_VARS)
    if iid:
        config = merge(config, PER_INST_VARS.get(iid))
    if resource:
        ensure('type' in resource, "given resource has no type information!")
        config = merge(config, PER_TYPE_VARS.get(resource['type']))
    return config
'''
