from os.path import join
from . import conf, utils, context, terraform
from .utils import ensure, threadm, lfilter
import os, json
from functools import partial, wraps, reduce
from collections import OrderedDict

def gen_path_to_org_file(oname): # returns a path to an extant file
    path_list = [
        join(conf.ORG_DIR, oname + ".yaml"),
        join(conf.TEST_FIXTURE_DIR, oname + '.yaml')
    ]
    path = utils.firstnn(os.path.exists, path_list)
    ensure(path, "failed to find org file: %s" % ', '.join(path_list))
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

def project_list(oname=None):
    defaults, odata = all_project_data(oname)
    return list(odata.keys())

def project_data(pname, oname=None):
    defaults, odata = all_project_data(oname)
    ensure(pname in odata, "project %r not found. available projects: %s" % (pname, ", ".join(odata.keys())))
    return odata[pname]

def mk_iid(pname, iname):
    pname, iname = threadm((pname, iname), str, 'lower', 'strip')
    ensure(pname and iname, "both a project name `pname` and instance name `iname` are required to create an instance-id `iid`")
    return "%s--%s" % (pname, iname)

#
#
#

def instance_path(iid, fname=None, create_dirs=False):
    "returns the path to project instance directory"
    path = join(conf.INSTANCE_DIR, iid)
    create_dirs and utils.mkdirs(path)
    return join(path, fname) if fname else path

def instance_list():
    if not os.path.exists(conf.INSTANCE_DIR):
        return []
    known_projects = project_list()
    def fn(fname):
        "an instance directory looks like 'pname--iname'"
        bits = fname.split('--')
        if len(bits) > 1 and bits[0] in known_projects:
            return os.path.isdir(join(conf.INSTANCE_DIR, fname))
    return lfilter(fn, os.listdir(conf.INSTANCE_DIR))

def instance_exists(iid):
    return os.path.exists(instance_path(iid))

def requires_instance(fn):
    @wraps(fn)
    def wrapper(iid, oname, *args, **kwargs):
        ensure(instance_exists(iid), "instance does not exist: %s" % iid)
        return fn(iid, oname, *args, **kwargs)
    return wrapper

def write_file(iid, filename, filedata):
    "writes a file to the project instance directory, returns the path written"
    path = instance_path(iid, filename, create_dirs=True)
    open(path, 'w').write(filedata) # insist on bytes?
    return path

def new_instance_data(iid, oname=None):
    """returns a snapshot of data about a project instance.
    this data could be used to compare with existing and generate updates"""
    pname = utils.parse_iid(iid)[0]
    pdata = project_data(pname, oname)

    # config + project def => instance_data => terraform/cloudformation/whatever template
    ctx = context.build(iid, pdata)

    return {
        # list of resources
        'pdata': pdata,

        # convenience, list of resource *types* (vagrant, ec2, etc)
        'pdata-resource-list': [resource['type'] for resource in pdata],

        # convenience, map of resource types -> resource
        # warn! lossy for projects with multiple resources of the same type!
        'pdata-resource-map': OrderedDict((r['type'], r) for r in pdata),

        'context': ctx,
    }

def instance_data_path(iid, oname=None):
    return instance_path(iid, 'instance-data.json')

def instance_data(iid, oname=None):
    """returns a map of data about the project instance, including the
    context used to build the terraform project and the project data."""
    return json.load(open(instance_data_path(iid), 'r'))

#
#
#

def terraform_configurator(iid, idata):
    results = {}
    # write a terraform template and init it, if possible
    tform_data = terraform.template(idata)
    if tform_data:
        tform_file_path = write_file(iid, iid + ".tf.json", json.dumps(tform_data, indent=4))
        # TODO: ns this to 'tform' perhaps
        results['tform-template'] = (tform_file_path, tform_data)
        utils.local_cmd("terraform init", cwd=instance_path(iid))
    return results

def project_configurator(iid, idata):
    # write the instance data to file
    write_file(iid, 'instance-data.json', json.dumps(idata))
    pc = idata['context'].get('project')
    if pc:
        # clone any configured formulas
        utils.run_script("clone-repo.sh", instance_path(iid), params=(pc['formula-name'], pc['formula']))
    return {}

def vagrant_configurator(iid, idata):
    return {}

def new_instance(pname, iname, overwrite=False):
    "creates a new instance of a project, returning a map of {data-name: (path-to-data, data)}"
    iid = mk_iid(pname, iname)
    not overwrite and ensure(not instance_exists(iid), "instance exists: %s" % instance_path(iid))

    # create/update the instance data
    idata = new_instance_data(iid)

    # run/re-run configuration using updated instance data
    configurator_list = [
        project_configurator,
        terraform_configurator,
        vagrant_configurator,
    ]
    # copy the idata so it doesn't get modified
    results = reduce(utils.merge, [fn(iid, utils.deepcopy(idata)) for fn in configurator_list])

    return results

def update_instance(iid):
    pname, iname = utils.parse_iid(iid)
    return new_instance(pname, iname, overwrite=True)

#
#
#

def resource(iid_or_idata, required_resource):
    iid = idata = None
    if isinstance(iid_or_idata, dict):
        idata = iid_or_idata
        iid = idata['context']['iid']
    else:
        iid = iid_or_idata
        idata = instance_data(iid)
    return lfilter(lambda r: r['type'] == required_resource, idata['pdata'])

def has_all_resources(iid, required_resource_list):
    "returns a subset of `required_resource_list` that are missing from project's instance data"
    resource_list = instance_data(iid)['pdata-resource-list']
    # all given resources are present in project's instance data
    return set(required_resource_list).difference(set(resource_list))
