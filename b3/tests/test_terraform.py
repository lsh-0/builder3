from b3 import project, context, terraform
import json

def test_two():
    pname = 'tform-p1'
    iid = project.mk_iid(pname, 'test')
    pdata = project.project_data(pname, oname='test-terraform-project')
    ctx = context.build(iid)
    expected = json.loads(r'''{
    "provider": {
        "aws": {
            "region": "ap-southeast-2",
            "profile": "default",
            "version": "~> 1.27"
        }
    },
    "resource": [
        {
            "aws_key_pair": {
                "r1--keypair": {
                    "key_name": "r1--keypair",
                    "public_key": ""
                }
            }
        },
        {
            "aws_security_group": {
                "r1--security-group": {
                    "name": "r1--security-group",
                    "vpc_id": "vpc-67e85103",
                    "ingress": [
                        {
                            "from_port": 22,
                            "to_port": 22,
                            "protocol": "tcp",
                            "cidr_blocks": [
                                "0.0.0.0/0"
                            ],
                            "ipv6_cidr_blocks": [
                                "::/0"
                            ]
                        }
                    ],
                    "egress": [
                        {
                            "from_port": 0,
                            "to_port": 0,
                            "protocol": "-1",
                            "cidr_blocks": [
                                "0.0.0.0/0"
                            ]
                        }
                    ]
                }
            }
        },
        {
            "aws_instance": {
                "r1": {
                    "ami": "ami-23c51c41",
                    "instance_type": "t2.nano",
                    "key_name": "r1--keypair",
                    "tags": [
                        {
                            "Name": "tform-p1--test--1"
                        },
                        {
                            "Project": "tform-p1"
                        },
                        {
                            "Instance Name": "test"
                        },
                        {
                            "Node": 1
                        }
                    ],
                    "security_groups": [
                        "${aws_security_group.r1--security-group.name}"
                    ],
                    "provisioner": {
                        "remote-exec": {
                            "inline": [
                                "echo 'hello, world!'",
                                "whoami",
                                "uname -a"
                            ],
                            "connection": {
                                "type": "ssh",
                                "user": "ubuntu",
                                "private_key": "${file(\"/media/sdb1/alice/dev/python/builder3/instances/tform-p1--test/tform-p1--test_rsa\")}"
                            }
                        }
                    }
                }
            }
        }
    ],
    "output": [
        {
            "public-ip": {
                "value": "${aws_instance.r1.public_ip}"
            }
        }
    ]
    }''')
    actual = terraform.pdata_to_tform(pdata, ctx)
    actual['resource'][0]['aws_key_pair']['r1--keypair']['public_key'] = ""
    assert expected == actual
