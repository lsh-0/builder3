from . import project, conf
from .utils import lfilter
from .remote_utils import ssh_conn, remote

STRAPPABLE_BOOTS = [
    'ec2',
    'vagrant',
    'droplet',
    'actual',
]

def bootstrap_actual(iid, idata):
    """To bootstrap an actual machine we need to:
* login as root or be able to become root
* upload the bootstrap script
* run the bootstrap script
* log in with the standard 'deploy-user' ('luke') afterwards"""

    if iid == 'work--juniper':
        with ssh_conn('10.1.1.88', conf.BOOTSTRAP_USER, '/home/luke/.ssh/id_rsa'):
            remote('cat /proc/cpuinfo | grep processor')

def bootstrap(iid):
    idata = project.instance_data(iid)
    project_resources = idata['pdata'].values()
    resource_list = lfilter(lambda r: r['type'] in STRAPPABLE_BOOTS, project_resources)
    print('bootstrap-able resources:', resource_list)
    bootstrap_actual(iid, idata)
