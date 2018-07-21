import os
from . import conf, project
from .utils import ensure
from collections import OrderedDict
import configparser
import logging

LOG = logging.getLogger(__name__)

def read_inventory(path=None):
    path = path or conf.INVENTORY_FILE
    if not os.path.exists(path):
        LOG.warn("inventory file not found: %s" % path)
        return OrderedDict()
    inv = configparser.ConfigParser()
    inv.read_file(open(path, 'r'))
    # we accept and return simple datastructures, not ConfigParser instances
    return OrderedDict([(section, OrderedDict(section_body)) for section, section_body in inv.items()])

def write_inventory(invdict, path=None):
    ensure(isinstance(invdict, dict), "given inventory is not a dictionary")
    path = path or conf.INVENTORY_FILE
    inv = configparser.ConfigParser()
    inv.read_dict(invdict)
    with open(path, 'w') as configfile:
        inv.write(configfile)
    return path

def instance_groups(iid):
    pname, iname = project.parse_iid(iid)[:2] # foo--bar
    return [
        'all', # simple bucket of 'all' instances
        pname, # group for instances of project 'foo'
        iname, # group for instances called 'bar' (or 'prod' or 'staging' or ...)
        iid,   # a group of it's own
    ]

def add_to_inventory(iid, path=None):
    # if shared inventory, sync inventory first
    inv = read_inventory()
    group_list = instance_groups(iid)

    # todo: pull these from the instance statefile
    public_ip = '0.0.0.0'
    ssh_port = 22

    for group_name in group_list:
        grp = inv.get(group_name, OrderedDict())

        # TODO: iid here should be replaced with iid--nodeid
        grp[iid] = "%s:%s" % (public_ip, ssh_port)
        inv[group_name] = grp

    write_inventory(inv, path)
    return inv
