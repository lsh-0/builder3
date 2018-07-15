from . import aws, project
import os
import logging

LOG = logging.getLogger(__name__)

def keypair_path(iid):
    return project.project_path(iid, iid + "_rsa")

def create_keypair(iid, region):
    "creates the ec2 keypair and writes it to s3"
    expected_key = keypair_path(iid)
    pub_path = expected_key + ".pub"
    if os.path.exists(expected_key):
        LOG.info('keypair, found existing: %s', expected_key)
        return expected_key, pub_path

    LOG.info('keypair, downloading new')
    ec2 = aws.boto_conn('ec2', region)
    keypair = ec2.create_key_pair(KeyName=iid)

    # py3 issue here: https://github.com/boto/boto/issues/3782
    # key.save(config.KEYPAIR_PATH) # exclude the filename
    #keypair.material = keypair.material.encode()
    open(expected_key, 'w').write(keypair.key_material)
    os.chmod(expected_key, 0o600)

    cmd = "ssh-keygen -y -f %s > %s" % (expected_key, pub_path)
    os.system(cmd)
    
    return expected_key, pub_path
