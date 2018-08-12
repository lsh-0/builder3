from . import utils
from .utils import ensure
from functools import reduce

AMI_MAP = {
    'ubuntu-16.04': {
        'ap-southeast-2': 'ami-47c21a25'
    },
    'ubuntu-18.04': {
        'ap-southeast-2': 'ami-23c51c41'
    }
}

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
    return utils.dictfilterv(lambda v: v.get('type') == typename, pdata)

#
#
#


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
    ensure('vpc' in ec2_resource_data, "no 'vpc' entry found") # replace with proper schema validation
    resource_name = ec2_resource_name + "--security-group" # 'my-vm-security-group'
    security_group = {
        "name": resource_name,
        # "description": "..." # don't do this. changing description will force a new resource.
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
    keypair = {
        "key_name": resource_name,
        "public_key": ctx['keypair']['pub']
    }
    return resource_name, keypair

def ssh_connection(ctx):
    return {
        'type': 'ssh',
        'user': 'ubuntu', # ami dependent
        'private_key': '${file("%s")}' % ctx['keypair']['pem']
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

def ec2_instance(resource_name, resource_data, ctx, node):
    "returns a single `aws_instance` resource and a single `aws_security_group` resource"

    security_group_name, security_group = _ec2_security_group(resource_name, resource_data, ctx)
    keypair_name, keypair = _ec2_keypair(resource_name, resource_data, ctx)

    region = resource_data['region']
    image_id = resource_data['image']['id']
    aws_instance = {
        "ami": AMI_MAP[image_id][region],
        "instance_type": resource_data['size'],
        "key_name": keypair_name,
        "tags": [
            {"Name": "%s--%s" % (ctx['iid'], node)},
            {"Project": ctx['project-name']},
            {"Instance Name": ctx['instance-name']},
            {"Node": node},
        ],
        "security_groups": ["${aws_security_group.%s.name}" % security_group_name],
        "provisioner": {"remote-exec": say_hello_world(ctx)},
    }
    return {
        "resource": [
            {"aws_key_pair": {keypair_name: keypair}},
            {'aws_security_group': {security_group_name: security_group}},
            {'aws_instance': {resource_name: aws_instance}},
        ],
        "output": [
            {"public-ip": {"value": "${aws_instance.%s.public_ip}" % resource_name}}
        ]
    }

def ec2_resources(pdata, ctx):
    "returns a mixed list of `aws_instance`, `aws_security_group` and `aws_key_pair` resources"
    vms = typefilter(pdata, 'ec2')
    retval = []
    for node, rname_rdata in enumerate(vms.items()):
        node += 1
        rname, rdata = rname_rdata
        retval.append(ec2_instance(rname, rdata, ctx, node))
    return utils.deepmerge(*retval)

def vpc_resources(pdata, ctx):
    return {
        'resource': [
            #{'foo': 'bar'}
        ],
        'output': [
            #{'basdef': {"value": 'asdfasdf'}}
        ]
    }

def aws_providers(pdata, ctx):
    provider = {
        "region": "ap-southeast-2",
        "profile": "default",
        # "shared_credentials_files": "~/.aws/credentials", # default

        "version": "~> 1.27",
    }
    return {
        "provider": {"aws": provider}
    }

TERRAFORMABLE_TYPES = [
    'ec2', 'vpc'
]

def terraformable(pdata):
    for resource_name, resource in pdata.items():
        if 'type' in resource and resource['type'] in TERRAFORMABLE_TYPES:
            return True
    return False

def template(idata):
    "translates project data into a structure suitable for terraform"
    pdata, ctx = idata['pdata'], idata['context']
    if not terraformable(pdata):
        return {}
    expansions = [
        aws_providers,
        ec2_resources,
        vpc_resources,
    ]
    expansions = [fn(pdata, ctx) for fn in expansions]
    return utils.deepmerge(*expansions)
