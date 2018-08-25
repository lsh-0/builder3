from fabric.api import task, local
from b3 import project, keypair, bootstrap as b3_bootstrap
from b3.utils import ensure, cpprint, BldrAssertionError, lfilter
from functools import wraps
from . import utils

def buserr(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return cpprint(fn(*args, **kwargs))
        except BldrAssertionError as err:
            print('error -', err)
            exit(1)
        except KeyboardInterrupt:
            print('interrupt')
            exit(1)
    return wrapper

task = buserr(task)

def pick_project():
    return 'p1'

def pick_iname():
    return 'foo'

#
#
#

@task
def pdata(pname):
    cpprint(project.project_data(pname))

@task
def defaults(oname=None):
    defaults, _ = project.all_project_data(oname)
    cpprint(defaults)

@task
def new(pname=None, iname=None):
    pname = pname or pick_project()
    iname = iname or pick_iname()
    iid = project.mk_iid(pname, iname)

    ensure(not project.instance_exists(iid), "instance exists, use 'update'")
    cpprint(project.new_instance(pname, iname))
    print(project.instance_path(iid))

@task
def update(iid):
    cpprint(project.update_instance(iid))
    print(project.instance_path(iid))

def sshable(resource):
    return resource['type'] in [
        'ec2',
        'vagrant'
    ]

@task
def ssh(iid, target=0xDEADBEEF):
    idata = project.instance_data(iid)
    targets = lfilter(sshable, idata['pdata-list'])
    target = utils.pick('project resources', targets, target)
    public_ip = target['public_ip']
    username = target['username']
    _, private_key_path = keypair.keypair_path(iid)
    local('ssh %s@%s -i %s' % (username, public_ip, private_key_path))  # , pty=True)

def bootstrappable(resource):
    return resource['type'] in [
        'ec2',
        'vagrant',
        'droplet',
        'actual',
    ]
    
@task
def bootstrap(iid, target=0xDEADBEEF):
    idata = project.instance_data(iid)
    targets = lfilter(bootstrappable, idata['pdata-list'])
    target = utils.pick('project resources', targets, target)
    b3_bootstrap.bootstrap(iid, idata, target)
