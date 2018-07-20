from . import keypair

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
    ctx = {
        'iid': iid,
        'ami-map': ami_map(),
        'keypair': lazy_keypair(iid),
    }
    return ctx
