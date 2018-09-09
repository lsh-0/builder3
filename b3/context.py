from . import keypair, utils, conf
from collections import OrderedDict

def ec2_context(iid, pdata):
    return {}

def vm_context(iid, pdata):
    """idempotent, will not create multiple keypairs.
    it will create multiple dictionaries with the same data at different paths 
    in the context if you have multiple ec2 instances, or multiple vm types, like ec2, droplet, etc"""
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
    "generates a dictionary used to create and update infrastructure"
    pname, iname = utils.parse_iid(iid)[:2]
    ctx = {
        'iid': iid,
        'project-name': pname,
        'instance-name': iname,
    }
    per_type_context = OrderedDict([
        ('ec2', [vm_context, ec2_context]),
    ])
    for resource_name, resource_data in pdata.items():
        rtype = resource_data['type']
        build_context_fn_lst = per_type_context[rtype] if rtype in per_type_context else []
        if not isinstance(build_context_fn_lst, list):
            build_context_fn_lst = [build_context_fn_lst]
        for build_context_fn in build_context_fn_lst:
            ctx[rtype] = ctx.get(rtype, {})
            ctx[rtype].update(build_context_fn(iid, pdata))
    return ctx
