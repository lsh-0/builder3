from fabric.api import task, local
import b3
import b3.bootstrap
from b3 import project, keypair
from b3.utils import ensure, cpprint, BldrAssertionError
from functools import wraps

def buserr(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return cpprint(fn(*args, **kwargs))
        except BldrAssertionError as err:
            print('error -', err)
    return wrapper

#task = task(buserr)

def pick_project():
    return 'p1'

def pick_iname():
    return 'foo'

#
#
#

@task
@buserr
def pdata(pname):
    cpprint(project.project_data(pname))

@task
@buserr
def defaults(oname=None):
    defaults, _ = project.all_project_data(oname)
    cpprint(defaults)

@task
@buserr
def new(pname=None, iname=None):
    pname = pname or pick_project()
    iname = iname or pick_iname()
    iid = project.mk_iid(pname, iname)

    ensure(not project.instance_exists(iid), "instance exists, use 'update'")
    cpprint(project.new_instance(pname, iname))
    print(project.instance_path(iid))

@task
@buserr
def update(iid):
    cpprint(project.update_instance(iid))
    print(project.instance_path(iid))

@task
@buserr
def ssh(iid, node=1):
    idata = project.instance_data(iid)
    public_ip = idata['ec2'][node]['public_ip']
    username = idata['ec2']['username']
    _, private_key_path = keypair.keypair_path(iid)
    local('ssh %s@%s -i %s' % (username, public_ip, private_key_path))  # , pty=True)

@task
@buserr
def bootstrap(iid):
    b3.bootstrap.bootstrap(iid) # urgh
