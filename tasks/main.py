from fabric.api import task as fabtask
from b3 import project, keypair, bootstrap as b3_bootstrap, conf, terraform as b3_terraform
from b3.utils import ensure, cpprint, BldrAssertionError, lfilter, local_cmd, run_script, repo_name
from functools import wraps
from . import utils, vagrant as vagrant_logic

def task(fn):
    @fabtask
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            resp = fn(*args, **kwargs)
            return cpprint(resp)
        except BldrAssertionError as err:
            print('error:', err)
            exit(1)
        except KeyboardInterrupt:
            print(' keyboard interrupt')
            exit(1)
    return wrapper

def pick_project():
    print('project')
    _, all_projects = project.read_org_file(conf.DEFAULT_PROJECT_FILE)
    return utils.pick('projects', list(all_projects.keys()))

def pick_iname():
    print('instance name')
    return utils.prompt()

def bootstrappable(resource):
    return resource['type'] in [
        'ec2',
        'vagrant',
        'droplet',
        'actual',
    ]

def requires_instance(fn):
    @wraps(fn)
    def _wrapper(iid=None, *args, **kwargs):
        known_instances = project.instance_list()
        if not iid:
            iid = utils.pick('instance', known_instances)
        ensure(iid in known_instances, "that is not a known instance")
        return fn(iid, *args, **kwargs)
    return _wrapper

def requires_project(fn):
    @wraps(fn)
    def _wrapper(pname=None, *args, **kwargs):
        known_projects = project.project_list()
        if not pname:
            pname = utils.pick('project', known_projects)
        ensure(pname in known_projects, "not a known project")
        return fn(pname, *args, **kwargs)
    return _wrapper

def requires_resources(*resource_list):
    def _wrap1(fn):
        @wraps(fn)
        def _wrap2(iid, *args, **kwargs):
            missing_resources = project.has_all_resources(iid, resource_list)
            ensure(len(missing_resources) == 0, \
                   "task %r requires missing resources: %s (do you need to run 'update'?)" % (fn.__name__, ", ".join(missing_resources)))
            return fn(iid, *args, **kwargs)
        return _wrap2
    return _wrap1

#
#
#

@task
@requires_project
def pdata(pname):
    "list project data"
    return project.project_data(pname)

@task
def defaults(oname=None, resource=None):
    "list default project data"
    defaults, _ = project.all_project_data(oname)
    if resource:
        ensure(resource in defaults, "resource %r not found" % resource)
        return defaults[resource]
    return defaults

@task
def instances():
    "list known instances"
    return project.instance_list()

@task
@requires_instance
def instance_data(iid):
    "list project instance state"
    cpprint(project.new_instance_data(iid))
    print()
    return project.instance_data_path(iid) 

@task
def new(pname=None, iname=None):
    "create new project instance"
    pname = pname or pick_project()
    iname = iname or pick_iname()
    iid = project.mk_iid(pname, iname)

    ensure(not project.instance_exists(iid), "instance exists, use 'update'")
    cpprint(project.new_instance(pname, iname))
    return project.instance_path(iid)

@task
@requires_instance
def update(iid):
    "update project instance"
    cpprint(project.update_instance(iid))
    return project.instance_path(iid)

@task
@requires_instance
def ssh(iid, target=0xDEADBEEF):
    "ssh into project instance"

    def sshable(resource):
        return resource['type'] in [
            'ec2',
            'vagrant'
        ]

    idata = project.instance_data(iid)
    targets = lfilter(sshable, idata['pdata'])
    target = utils.pick('project resources', targets, target, auto_pick=True)
    public_ip = target['public_ip']
    username = target['username']
    _, private_key_path = keypair.keypair_path(iid)
    local_cmd('ssh %s@%s -i %s' % (username, public_ip, private_key_path))

@task
@requires_instance
def bootstrap(iid, target=0xDEADBEEF):
    "bootstrap project instance"
    idata = project.instance_data(iid)
    targets = lfilter(bootstrappable, idata['pdata'])
    target = utils.pick('project resources', targets, target, auto_pick=True)
    b3_bootstrap.bootstrap(iid, idata, target)

@task
@requires_instance
def plan(iid):
    idata = project.instance_data(iid)
    cpprint(b3_terraform.template(idata))
    local_cmd('terraform plan', project.instance_path(iid))

@task
@requires_instance
def terraform(iid, cmd):
    "does a 'terraform apply' and then updates the instance data"
    dispatch = {
        'apply': project.apply_update
    }
    ensure(cmd in dispatch, "unknown command %r" % cmd) 
    return dispatch[cmd](iid)
    
@task
@requires_project #@requires_resources('vagrant', 'project-config') # TODO: this checks the pdata, but the ctx values are used
def vagrant(pname, cmd='up'):
    "calls custom Vagrant file with a bunch of ENVVARs set."
    cmd = str(cmd).strip().lower()
    iname = 'vagrant'
    iid = project.mk_iid(pname, iname) # "projectname--vagrant"
    
    cfg = project.project_data_map(pname)
    envvars = {
        'BLDR_PNAME': pname,
        'BLDR_INAME': iname,
        'BLDR_IID': iid,
        'BLDR_VAGRANT_BOX': cfg['vagrant']['box'],
        'BLDR_PROJECT_REPO': repo_name(cfg['project-config']['project-formula-url']),
        'BLDR_DEPLOY_USER': conf.DEPLOY_USER,
    }

    vagrant_logic.write_etc_salt_minion(pname)
    if cmd in ['provision', 'up', 'reload']:
        vagrant_logic.clone_repos(pname)

    cmd = ['%s="%s"' % keyval for keyval in envvars.items()] + ["vagrant", cmd]
    cmdstr = " ".join(cmd)
    local_cmd(cmdstr)

@task
@requires_project
def new_formula(pname):
    "creates a new project formula"
    return run_script('new-project.sh', params=(pname,))
