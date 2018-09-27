from . import conf
from .utils import ensure, parse_iid
from .remote_utils import ssh_conn_password, run_script


def bootstrap_actual(iid, idata, resource):
    """To bootstrap an actual machine we need to:
    * login as root or be able to become root
    * upload the bootstrap script
    * run the bootstrap script
    * log in with the standard 'deploy-user' ('luke') afterwards"""

    conns = {
        'work--juniper': {
            'ip': '10.1.1.88'
        },
        'home--rama': {
            'ip': '10.1.1.198'
        }
    }

    ensure(iid in conns, "cannot bootstrap %r, unknown IP")

    with ssh_conn_password(conns[iid]['ip'], conf.BOOTSTRAP_USER, conf.BOOTSTRAP_PASS):
        pname, iname = parse_iid(iid)
        run_script('bootstrap.sh', pname, iname, conf.DEPLOY_USER)

def bootstrap(iid, idata, resource):
    dispatch = {
        'actual': bootstrap_actual
    }
    return dispatch[resource['type']](iid, idata, resource)
