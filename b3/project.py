from os.path import join
from . import conf, utils
from .utils import ensure
import os, copy
from functools import partial
from pprint import pprint
from collections import OrderedDict

def gen_path_to_org_file(oname): # returns a path to an extant file
    path_list = [
        join(conf.ORG_DIR, oname + ".yaml"),
        join(conf.TEST_FIXTURE_DIR, oname + '.yaml')
    ]
    path = utils.firstnn(os.path.exists, path_list)
    ensure(path, "failed to find a project file at any of these paths: %s" % ', '.join(path_list), ValueError)
    return path

def read_org_file(oname): # returns a list of raw project descriptions
    pdata = utils.load_yaml(gen_path_to_org_file(oname))
    # TODO: test correctness of project file
    defaults = pdata.pop('defaults')
    return defaults, pdata

#
#
#

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
    resource = utils.deepcopy(rdefaults)
    resource.update(struct)
    return resource

# cacheable
def all_project_data(oname=None):
    defaults, odata = read_org_file(oname or conf.DEFAULT_PROJECT_FILE)
    visit_fn = partial(expand_type, defaults)
    new_defaults = visit(defaults, visit_fn)
    visit_fn = partial(expand_type, new_defaults)
    return new_defaults, OrderedDict([(pname, visit(pdata, visit_fn)) for pname, pdata in odata.items()])

def project_data(pname, oname=None):
    defaults, odata = all_project_data(oname)
    ensure(pname in odata, "project %r not found. available projects: %s" % (pname, ", ".join(odata.keys())))
    return odata[pname]
