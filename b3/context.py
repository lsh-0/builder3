import os
from . import keypair, utils
from collections import OrderedDict

def ec2_context(iid, pdata, resource):
    return {}

def vm_context(iid, pdata, _):
    """idempotent, will not create multiple keypairs.
    it will create multiple dictionaries with the same data at different paths 
    in the context if you have multiple ec2 instances, or multiple vm types, like ec2, droplet, etc"""
    pub_path, pem_path = keypair.create_keypair(iid) # idempotent

    # makes absolute pem path relative to INSTANCE_DIR/$instance
    local_pem_path = os.path.basename(pem_path)

    return {
        'keypair': {
            'pub': open(pub_path, 'r').read(),
            'pem': local_pem_path
        }
    }

def project_context(iid, pdata, resource):
    repo = resource['project-formula-url']
    # just the formula name, sans any '.git' ext
    repo_name = os.path.splitext(os.path.basename(repo))[0]
    return {
        'formula': repo,
        'formula-name': repo_name
    }

def build(iid, pdata):
    "generates a dictionary used to create and update infrastructure"
    per_type_context = OrderedDict([
        ('project-config', project_context),
        ('ec2', [vm_context, ec2_context]),
    ])
    ctx = {}
    for resource in pdata:
        rtype = resource['type']
        build_context_fn_lst = per_type_context[rtype] if rtype in per_type_context else []
        if not isinstance(build_context_fn_lst, list):
            build_context_fn_lst = [build_context_fn_lst]
        for build_context_fn in build_context_fn_lst:
            ctx[rtype] = ctx.get(rtype, {})
            ctx[rtype].update(build_context_fn(iid, pdata, resource))

    # and some exceptions to the rule for convenience:
    pname, iname = utils.parse_iid(iid)[:2]
    ctx.update({
        'iid': iid,
        'project-name': pname,
        'instance-name': iname,
    })
    return ctx
