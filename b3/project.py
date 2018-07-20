from os.path import join
from . import conf, utils
from .utils import ensure, thread
import os
from functools import partial
from collections import OrderedDict

def gen_path_to_org_file(oname): # returns a path to an extant file
    path_list = [
        join(conf.ORG_DIR, oname + ".yaml"),
        join(conf.TEST_FIXTURE_DIR, oname + '.yaml')
    ]
    path = utils.firstnn(os.path.exists, path_list)
    ensure(path, "failed to find a project: %s" % ', '.join(path_list))
    return path

def read_org_file(oname): # returns a list of raw project descriptions
    pdata = utils.load_yaml(gen_path_to_org_file(oname))
    # TODO: test correctness of project file
    defaults = pdata.pop('defaults')
    return defaults, pdata

def visit(val, fn):
    val = fn(val)
    if isinstance(val, dict):
        newval = {key: visit(subval, fn) for key, subval in val.items()}
    elif isinstance(val, list):
        newval = [visit(subval, fn) for subval in val]
    else:
        newval = fn(val)
    return newval

#
#
#

def is_type(struct):
    return isinstance(struct, dict) and 'type' in struct

def expand_type(defaults, struct):
    if not is_type(struct):
        return struct
    rtype = struct['type']
    ensure(rtype in defaults, "type %r for %r not found. a type definition must be declared *before* it is used." % (rtype, struct))
    rdefaults = defaults[rtype]
    resource = utils.deepcopy(rdefaults)
    resource.update(struct)
    return resource

# cacheable
def all_project_data(oname=None):
    "returns a pair of (defaults, all project data)"
    defaults, odata = read_org_file(oname or conf.DEFAULT_PROJECT_FILE)

    # process defaults, recursively expanding any types
    visit_fn = partial(expand_type, defaults)
    new_defaults = visit(defaults, visit_fn)

    # process project data using processed defaults
    visit_fn = partial(expand_type, new_defaults)
    odata = OrderedDict([(pname, visit(pdata, visit_fn)) for pname, pdata in odata.items()])

    return new_defaults, odata

def project_data(pname, oname=None):
    defaults, odata = all_project_data(oname)
    ensure(pname in odata, "project %r not found. available projects: %s" % (pname, ", ".join(odata.keys())))
    return odata[pname]

def mkiid(pname, iname):
    pname = thread(pname, str, 'lower', 'strip')
    iname = thread(iname, str, 'lower', 'strip')
    ensure(pname and iname, "both a project name `pname` and instance name `iname` are required to create an instance-id `iid`")
    return "%s--%s" % (pname, iname)

#
#
#

def instance_path(iid, fname=None, create_dirs=True):
    "returns the path to project instance directory"
    path = join(conf.INSTANCE_DIR, iid)
    create_dirs and utils.mkdirs(path)
    return join(path, fname) if fname else path

def write_file(iid, filename, filedata):
    "writes a file to the project instance directory, returns the path written"
    path = instance_path(iid, filename)
    open(path, 'w').write(filedata) # insist on bytes?
    return path

def instance_exists(iid):
    return os.path.exists(instance_path(iid))
