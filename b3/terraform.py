from . import utils, project
from .utils import ensure
import json
from functools import reduce

def process(pdata, fnlist, shrink=False):
    """passes the project data through a list of functions, each function returning a map, 
    and then shrinks the list of maps into a single map"""
    plist = []
    for fn in fnlist:
        ret = fn(pdata)
        if not ret:
            continue
        ensure(isinstance(ret, dict), "return value of fn %s is not a dictionary: %s" % (fn, type(ret)))
        plist.append(ret)
    if plist and shrink:
        return reduce(utils.merge, plist)
    return plist

def typefilter(pdata, typename):
    "give a dict of project data, returns all top-level resources of given `typename`"
    return utils.dictfilterv(lambda v: v.get('type') == 'vm', pdata)

#
#
#

def write_template(iid, data):
    return project.write_file(iid, iid + ".tf.json", json.dumps(data, indent=4))

def mkport(port_data):
    if isinstance(port_data, dict):
        # assume the port data we've been given is complete
        return port_data
    elif isinstance(port_data, int):
        return {
            "from_port": port_data,
            "to_port": port_data,
            "protocol": "tcp",
            "cidr_blocks": ["0.0.0.0/0"], # ipv4 "anywhere"
            "ipv6_cidr_blocks": ["::/0"], # ipv6 "anywhere"
        }
    raise AssertionError("cannot handle port data of type %s: %s" % (type(port_data), port_data))

def _ec2_security_group(ec2_resource_name, ec2_resource_data, ctx):
    resource_name = ec2_resource_name + "--security-group" # 'my-vm-security-group'
    security_group = {
        "name": resource_name,
        #"description": "..." # don't do this. changing description will force a new resource.
        "vpc_id": ec2_resource_data['vpc']['id'],
        "ingress": [mkport(port_data) for port_data in ec2_resource_data['ports']],
        # Terraform will remove the default AWS egress rules (ALL) if we don't explicitly supply them
        # https://www.terraform.io/docs/providers/aws/r/security_group.html#description-2
        "egress": [
            {"from_port": 0, "to_port": 0, "protocol": "-1", "cidr_blocks": ["0.0.0.0/0"]}
        ]
    }
    return resource_name, security_group

def _ec2_keypair(resource_name, resource_data, ctx):
    resource_name = "%s--keypair" % resource_name
    keypair = ctx['keypair']()
    keypair = {
        "key_name": resource_name,
        "public_key": keypair['pub']
    }
    return resource_name, keypair

def ssh_connection(ctx):
    return {
        'type': 'ssh',
        'user': 'ubuntu', # ami dependent
        'private_key': '${file("%s")}' % ctx['keypair']()['pem']
    }

def say_hello_world(ctx):
    commands = [
        "echo 'hello, world!'",
        "whoami",
        "uname -a",
    ]
    return {
        "inline": commands,
        "connection": ssh_connection(ctx)
    }

def ec2_instance(resource_name, resource_data, ctx):
    "returns a single `aws_instance` resource and a single `aws_security_group` resource"
    
    security_group_name, security_group = _ec2_security_group(resource_name, resource_data, ctx)
    keypair_name, keypair = _ec2_keypair(resource_name, resource_data, ctx)

    region = resource_data['region']
    image_id = resource_data['image']['id']
    aws_instance = {
        "ami": ctx['ami-map'][image_id][region],
        "instance_type": resource_data['size'],
        "key_name": keypair_name,
        "tags": [
            {"Name": ctx['iid']}
        ],
        "security_groups": ["${aws_security_group.%s.name}" % security_group_name],
        "provisioner": {"remote-exec": say_hello_world(ctx)},
    }
    return [
        {"aws_key_pair": {keypair_name: keypair}},
        {'aws_security_group': {security_group_name: security_group}},
        {'aws_instance': {resource_name: aws_instance}},
    ]


def ec2_resources(pdata, ctx):
    "returns a mixed list of `aws_instance`, `aws_security_group` and `aws_key_pair` resources"
    vms = typefilter(pdata, 'vm')
    return utils.flatten([ec2_instance(rname, rdata, ctx) for rname, rdata in vms.items()])

def vpc_resources(pdata, ctx):
    return []

def aws_providers(pdata):
    provider = {
        "region": "ap-southeast-2",
        "profile": "default",
        #"shared_credentials_files": "~/.aws/credentials", # default
        
        "version": "~> 1.27",
    }
    return {"aws": provider}

def pdata_to_tform(pdata, ctx):
    "translates project data into a structure suitable for terraform"

    providers = [
        aws_providers
    ]
    providers = process(pdata, providers, shrink=True)

    resources = [
        ec2_resources,
        vpc_resources,
    ]
    resources = [fn(pdata, ctx) for fn in resources]
    resources = utils.flatten(filter(None, resources))

    return {
        "provider": providers,
        "resource": resources,
    }
