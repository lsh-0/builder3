from os.path import join
from . import conf, utils, terraform, keypair
from .utils import ensure, threadm, lmap, lfilter, first
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
# utils
# 

def _get_resource(pdata, resource_name):
    return first(filter(lambda r: r['type'] == resource_name, pdata))

def get_resource(iid_or_idata_or_pdata, resource_name):
    "returns the *first* resource in the pdata derived from the first argument whose 'type' attribute matches given 'resource_name'"
    dispatch = {
        # iid
        str: lambda: instance_data(iid_or_idata_or_pdata)['pdata'],
        # idata
        dict: lambda: iid_or_idata_or_pdata['pdata'],
        # pdata
        list: lambda: iid_or_idata_or_pdata
    }
    pdata = dispatch[type(iid_or_idata_or_pdata)]()
    return _get_resource(pdata, resource_name)

def get_resource_list(iid_or_idata_or_pdata, resource_name_list):
    "like `get_resource` but returns all resources of given type"
    pass

# TODO: this is checking context (static) vs project data (dynamic)
def has_all_resources(iid, required_resource_list):
    "returns a subset of `required_resource_list` that are missing from project's instance data"
    resource_list = instance_data(iid)['pdata-resource-list']
    # all given resources are present in project's instance data
    return set(required_resource_list).difference(set(resource_list))

def has_resource(iid, required_resource):
    "convenience. see has_all_resources"
    return has_all_resources(iid, [required_resource])

def ensure_has_resource(iid, *required_resource_list):
    missing_resources = has_all_resources(iid, required_resource_list)
    ensure(not missing_resources, "%r is missing resources: %s" % (iid, ", ".join(missing_resources)))
    return True

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

#
# 
#

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

def project_data_map(pname, oname=None):
    """WARNING: a project may have multiple resources of a give type. 
    this is for *convenience only* when we know for certain there is only ever a single instance of a given type"""
    pdata = project_data(pname, oname)
    return OrderedDict((r['type'], r) for r in pdata)

def mk_iid(pname, iname):
    pname, iname = threadm((pname, iname), str, 'lower', 'strip')
    ensure(pname and iname, "both a project name `pname` and instance name `iname` are required to create an instance-id `iid`")
    return "%s--%s" % (pname, iname)


"""

context

the 'context' is a subset of all available project and instance data.

the subset of data contains everything needed to create new, update and delete existing project instances.

it brings disparate data together, like project data and terraform state and public keys, etc

it contains convenience values - values derived from one or more other values.

the context is a snapshot of what the project data looked like at either creation time or after the last update. it doesn't otherwise change

the instance context may be bundled with the parsed project data and called `idata`.

"""

def terraform_init_ed(iid):
    return os.path.exists(join(instance_path(iid), ".terraform"))

def terraform_outputs(iid):
    "returns whatever outputs exists from terraform. if the instance hasn't been launched or has been destroyed, there won't be anything"
    if not terraform_init_ed(iid):
        return {}
    results = utils.local_cmd("terraform output -json", cwd=instance_path(iid), capture=True)
    return json.loads(results['stdout'])

def ec2_context(iid, pdata, resource):
    return {}

def vm_context(iid, pdata, _):
    """idempotent, will not create multiple keypairs.
    it will create multiple dictionaries with the same data at different paths 
    in the context if you have multiple ec2 instances, or multiple vm types, like ec2, droplet, etc"""
    pub_path, pem_path = keypair.create_keypair(iid) # idempotent

    # makes absolute pem path relative to INSTANCE_DIR/$instance
    local_pem_path = os.path.basename(pem_path)

    return {
        'keypair': {
            'pub': open(pub_path, 'r').read(),
            'pem': local_pem_path
        }
    }

def _formula_breakdown(url):
    return {
        'formula': url,
        'formula-name': utils.repo_name(url)
    }

def project_context(iid, pdata, resource):
    repo = resource['project-formula-url']
    # just the formula name, sans any '.git' ext
    repo_name = os.path.splitext(os.path.basename(repo))[0]
    return {
        'formula': repo,
        'formula-name': repo_name,
        'formula-dependencies': lmap(_formula_breakdown, resource.get('formula-dependencies'))
    }

def vagrant_context(iid, pdata, resource):
    return utils.deepcopy(resource)

def build(iid, pdata):
    "generates a dictionary used to create and update infrastructure"
    per_type_context = OrderedDict([
        ('project-config', project_context),
        ('ec2', [vm_context, ec2_context]),
        ('vagrant', vagrant_context),
    ])
    ctx = {}
    for resource in pdata:
        rtype = resource['type']
        build_context_fn_lst = per_type_context[rtype] if rtype in per_type_context else []
        if not isinstance(build_context_fn_lst, list):
            build_context_fn_lst = [build_context_fn_lst]
        for build_context_fn in build_context_fn_lst:
            ctx[rtype] = ctx.get(rtype, {})
            ctx[rtype].update(build_context_fn(iid, pdata, resource))

    # and some exceptions to the rule for convenience:
    pname, iname = utils.parse_iid(iid)[:2]
    ctx.update({
        'iid': iid,
        'project-name': pname,
        'instance-name': iname,
    })
    return ctx


#
# instances
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
    ctx = build(iid, pdata)

    return {
        # list of resources
        'pdata': pdata,

        # convenience, list of resource *types* (vagrant, ec2, etc)
        'pdata-resource-list': [resource['type'] for resource in pdata],

        # convenience, map of resource types -> resource
        # warn! lossy for projects with multiple resources of the same type!
        'pdata-resource-map': project_data_map(pname, oname),

        'context': ctx,

        # this is a bit meh.
        'state': terraform_outputs(iid)
    }

def instance_data_path(iid, oname=None):
    return instance_path(iid, 'instance-data.json')

# TODO: cache me
def instance_data(iid, oname=None):
    """returns a map of data about the project instance, including the
    context used to build the terraform project and the project data."""
    return json.load(open(instance_data_path(iid), 'r'))

#
# init/update/config of instances
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
# launch instances
#

def apply_update(iid):
    idata = instance_data(iid)
    if not terraform.terraformable(idata['pdata']):
        return {}
    #return utils.local_cmd("terraform apply -auto-approve", cwd=instance_path(iid))
    return utils.local_cmd("terraform apply", cwd=instance_path(iid))
