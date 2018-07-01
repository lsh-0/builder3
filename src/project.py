import conf
from os.path import join
from . import utils

def gen_path_to_org_file(oname): # returns a path to an extant file
    return join(conf.ORG_DIR, oname + ".yaml")

def read_org_file(oname): # returns a list of raw project descriptions
    return utils.load_yaml(gen_path_to_org_file(oname))

#
#
#

import copy
from functools import partial
from pprint import pprint

def deepcopy(d):
    return copy.deepcopy(d)

def visit(val, fn):
    val = fn(val)
    if isinstance(val, dict):
        newval = {key: visit(subval, fn) for key, subval in val.items()}
    elif isinstance(val, list):
        newval = [visit(subval, fn) for subval in val]
    else:
        newval = fn(val)
    return newval

def expand_type(defaults, struct):
    if not (isinstance(struct, dict) and 'type' in struct):
        return struct
    rtype = struct.pop('type')
    rdefaults = defaults[rtype]
    resource = deepcopy(rdefaults)
    resource.update(struct)
    return resource

def main():
    pdata = read_org_file('home')
    defaults = pdata.pop('defaults')

    visit_fn = partial(expand_type, defaults)
    new_defaults = visit(defaults, visit_fn)

    #pprint(('original',defaults))
    #pprint(('new',new_defaults))

    project = pdata['wowman']
    new_pdata = visit(project, partial(expand_type, new_defaults))

    pprint(('original', project))
    pprint(('new', new_pdata))
