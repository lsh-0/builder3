from . import project
from .utils import ensure
import os
from os.path import join
import logging

LOG = logging.getLogger(__name__)

def keypair_path(iid):
    path = project.instance_path(iid)
    pem_fname = iid + "_rsa"
    pub_fname = pem_fname + ".pub"
    return join(path, pub_fname), join(path, pem_fname)

def create_keypair(iid):
    """use ssh-keygen to generate a public+private keypair.
    pubkey is ultimately uploaded to instance and allows ssh login"""
    # -t type
    # -f output filename
    # -N passphrase (no passphrase '')
    pubkey, pemkey = keypair_path(iid)
    if os.path.exists(pemkey):
        # we can always derive the pubkey again with -y if it's missing
        return pubkey, pemkey
    # if pemkey exists, it *will* prompt you.
    cmd = "ssh-keygen -t rsa -f %s -N ''" % pemkey
    rc = os.system(cmd)
    ensure(rc == 0, "failed to generate keypair for %s: %s" % (pemkey, rc))
    ensure(os.path.exists(pubkey), "pubkey not found: %s" % pubkey)
    ensure(os.path.exists(pemkey), "pemkey not found: %s" % pemkey)

    # correct permissions on pemkey else ssh barfs
    cmd = "chmod 400 %s" % pemkey
    rc = os.system(cmd)
    ensure(rc == 0, "failed to set permissions on pemkey: %s" % pemkey)

    return pubkey, pemkey
