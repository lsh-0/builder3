from . import keypair, utils, conf
from collections import OrderedDict

def ec2_context(iid, pdata):
    pub_path, pem_path = keypair.create_keypair(iid) # idempotent

    # makes absolute pem path relative to INSTANCE_DIR
    local_pem_path = pem_path[len(conf.INSTANCE_DIR) + 1:]

    return {
        'keypair': {
            'pub': open(pub_path, 'r').read(),
            'pem': local_pem_path
        }
    }

def build(iid, pdata):
    "generates a dictionary used in creating terraform templates"
    pname, iname = utils.parse_iid(iid)[:2]
    ctx = {
        'iid': iid,
        'project-name': pname,
        'instance-name': iname,
    }
    per_type_context = OrderedDict([
        ('ec2', ec2_context),
    ])
    for resource_name, resource_data in pdata.items():
        rtype = resource_data['type']
        if rtype in per_type_context:
            ctx.update(per_type_context[rtype](iid, pdata))
    return ctx
