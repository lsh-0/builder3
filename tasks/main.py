from fabric.api import task as fabtask, local
from b3 import project, keypair, bootstrap as b3_bootstrap, conf
from b3.utils import ensure, cpprint, BldrAssertionError, lfilter
from functools import wraps
from . import utils

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

def sshable(resource):
    return resource['type'] in [
        'ec2',
        'vagrant'
    ]

def bootstrappable(resource):
    return resource['type'] in [
        'ec2',
        'vagrant',
        'droplet',
        'actual',
    ]

#
#
#

@task
def pdata(pname):
    return project.project_data(pname)

@task
def defaults(oname=None, resource=None):
    defaults, _ = project.all_project_data(oname)
    if resource:
        ensure(resource in defaults, "resource %r not found" % resource)
        return defaults[resource]
    return defaults

@task
def instances():
    return project.instance_list()

@task
def new(pname=None, iname=None):
    pname = pname or pick_project()
    iname = iname or pick_iname()
    iid = project.mk_iid(pname, iname)

    ensure(not project.instance_exists(iid), "instance exists, use 'update'")
    cpprint(project.new_instance(pname, iname))
    return project.instance_path(iid)

@task
def update(iid):
    cpprint(project.update_instance(iid))
    return project.instance_path(iid)

@task
def ssh(iid, target=0xDEADBEEF):
    idata = project.instance_data(iid)
    targets = lfilter(sshable, idata['pdata-list'])
    target = utils.pick('project resources', targets, target)
    public_ip = target['public_ip']
    username = target['username']
    _, private_key_path = keypair.keypair_path(iid)
    local('ssh %s@%s -i %s' % (username, public_ip, private_key_path))
    
@task
def bootstrap(iid, target=0xDEADBEEF):
    idata = project.instance_data(iid)
    targets = lfilter(bootstrappable, idata['pdata-list'])
    target = utils.pick('project resources', targets, target)
    b3_bootstrap.bootstrap(iid, idata, target)
