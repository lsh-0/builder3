# lets try and contain all references to Fabric to this file.
# we're using Fabric3 which is a python3 port of Fabric 1.x line
# and Fabric 2.x has been redeveloped as a thin layer over Invoke.
# Invoke is new and still immature and buggy in my opinion (2018-08)
import os
from .utils import ensure
from fabric.api import settings, run, sudo
from contextlib import contextmanager

@contextmanager
def ssh_conn(host_or_ip, user, pem_path, **kwargs):
    ensure(os.path.exists(pem_path), "given pem path doesn't exist: %s" % pem_path)
    params = {
        'user': user,
        'key_filename': pem_path,
        'host_string': host_or_ip,
    }
    params.update(kwargs)
    with settings(**params):
        yield

def remote(cmd):
    # requires a stack_conn
    return run(cmd)

def remote_sudo(cmd):
    # requires a stack_conn
    return sudo(cmd)
