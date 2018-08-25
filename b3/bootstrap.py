from . import conf
from .remote_utils import ssh_conn, run_script


def bootstrap_actual(iid, idata, resource):
    """To bootstrap an actual machine we need to:
    * login as root or be able to become root
    * upload the bootstrap script
    * run the bootstrap script
    * log in with the standard 'deploy-user' ('luke') afterwards"""
    if iid == 'work--juniper':
        with ssh_conn('10.1.1.88', conf.BOOTSTRAP_USER, '/home/luke/.ssh/id_rsa'):
            run_script('bootstrap.sh', conf.DEPLOY_USER)

def bootstrap(iid, idata, resource):
    dispatch = {
        'actual': bootstrap_actual
    }
    return dispatch[resource['type']](iid, idata, resource)
