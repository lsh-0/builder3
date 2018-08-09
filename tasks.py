from fabric.api import task, local
from b3 import project, context, terraform, keypair
from b3.utils import ensure, cpprint
from functools import wraps

# not working with @task atm
# https://github.com/pyinvoke/invoke/issues/555
def buserr(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return cpprint(fn(*args, **kwargs))
        except AssertionError as err:
            print(err)
    return wrapper

@task
@buserr
def foobar(p1):
    print(p1)
    raise AssertionError('baz')

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

def pick_project():
    return 'p1'

def pick_iname():
    return 'foo'

@task
def new(pname=None, iname=None, overwrite=False):
    pname = pname or pick_project()
    iname = iname or pick_iname()
    iid = project.mk_iid(pname, iname)
    not overwrite and ensure(not project.instance_exists(iid), "instance exists, use 'update'")
    ctx = context.build(iid)
    template = terraform.pdata_to_tform(project.project_data(pname), ctx)
    cpprint(template)
    path = terraform.write_template(ctx['iid'], template)
    print("wrote", path)
    return path

@task
def update(iid):
    pname, iname = project.parse_iid(iid)[:2]
    return new(pname, iname, overwrite=True)

@task
def ssh(iid, node=1):
    idata = context.instance_state(iid)
    public_ip = idata['ec2'][node]['public_ip']
    username = idata['ec2']['username']
    _, private_key_path = keypair.keypair_path(iid)
    local('ssh %s@%s -i %s' % (username, public_ip, private_key_path), pty=True)
