from . import keypair, project
from .utils import ensure

def ami_map():
    return {
        'ubuntu-16.04': {
            'ap-southeast-2': 'ami-47c21a25'
        },
        'ubuntu-18.04': {
            'ap-southeast-2': 'ami-23c51c41'
        }
    }

def lazy_keypair(iid):
    "called when an ec2 keypair is required by the template. if the template doesn't access the keypair, one won't be generated"
    def wrapped():
        pub_path, pem_path = keypair.create_keypair(iid) # idempotent
        return {
            'pub': open(pub_path, 'r').read(),
            'pem': pem_path,
        }
    return wrapped

def build(iid):
    "generates a dictionary used in creating terraform templates"
    pname, iname = project.parse_iid(iid)[:2]
    ctx = {
        'iid': iid,
        'project-name': pname,
        'instance-name': iname,
        'ami-map': ami_map(),
        'keypair': lazy_keypair(iid),
    }
    return ctx

def instance_state(iid):
    "returns a dictionary of values from a terraform statefile."
    ensure(project.instance_exists(iid), "instance %s must exist with a statefile" % iid)
    return {
        'username': 'ubuntu',
        'ec2': [
            {'public-ip': '0.0.0.0'}
        ]
    }
