from . import keypair, utils, conf

def ami_map():
    return {
        'ubuntu-16.04': {
            'ap-southeast-2': 'ami-47c21a25'
        },
        'ubuntu-18.04': {
            'ap-southeast-2': 'ami-23c51c41'
        }
    }

def write_keypair(iid):
    pub_path, pem_path = keypair.create_keypair(iid) # idempotent

    # makes absolute pem path relative to INSTANCE_DIR
    local_pem_path = pem_path[len(conf.INSTANCE_DIR) + 1:]
    return {
        'pub': open(pub_path, 'r').read(),
        'pem': local_pem_path
    }
    
def lazy_keypair(iid):
    "called when an ec2 keypair is required by the template. if the template doesn't access the keypair, one won't be generated"
    return lambda: write_keypair(iid)

def build(iid):
    "generates a dictionary used in creating terraform templates"
    pname, iname = utils.parse_iid(iid)[:2]
    ctx = {
        'iid': iid,
        'project-name': pname,
        'instance-name': iname,
        'ami-map': ami_map(),
        #'keypair': lazy_keypair(iid),
        'keypair': write_keypair(iid),
    }
    return ctx
