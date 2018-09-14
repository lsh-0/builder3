# lets try and contain all references to Fabric to this file.
# we're using Fabric3 which is a python3 port of Fabric 1.x line
# and Fabric 2.x has been redeveloped as a thin layer over Invoke.
# Invoke is new and still immature and buggy in my opinion (2018-08)
from datetime import datetime
import os
from os.path import join
from . import conf
from .utils import ensure, lmap
from fabric.api import settings, run, sudo
from fabric.operations import put #, get
from contextlib import contextmanager
import logging

LOG = logging.getLogger(__name__)

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

@contextmanager
def ssh_conn_password(host_or_ip, user, passwd, **kwargs):
    params = {
        'user': user,
        'password': passwd,
        'host_string': host_or_ip
    }
    params.update(kwargs)
    with settings(**params):
        yield

def remote_cmd(cmd):
    # requires a stack_conn
    return run(cmd)

def remote_sudo(cmd):
    # requires a stack_conn
    return sudo(cmd)

def upload_file(local_path, remote_path, use_sudo=False, label=None):
    "wrapper around fabric.operations.put"
    label = label or os.path.basename(local_path)
    msg = "uploading %s to %s" % (label, remote_path)
    LOG.info(msg)
    put(local_path=local_path, remote_path=remote_path, use_sudo=use_sudo)
    return remote_path

'''
def fab_put_data(data, remote_path, use_sudo=False):
    ensure(isinstance(data, bytes) or isstr(data), "data must be bytes or a string that can be encoded to bytes")
    data = data if isinstance(data, bytes) else data.encode()
    bytestream = BytesIO(data)
    label = "%s bytes" % bytestream.getbuffer().nbytes if gtpy2() else "? bytes"
    return fab_put(bytestream, remote_path, use_sudo=use_sudo, label=label)
'''

def _put_temporary_script(script_filename):
    local_script = join(conf.SCRIPTS_PATH, script_filename)
    ensure(os.path.exists(local_script), "could not find script: %s" % local_script)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    remote_script = join('/tmp', "%s-%s" % (os.path.basename(local_script), timestamp))
    return upload_file(local_script, remote_script)

def put_script(script_filename, remote_script):
    """uploads a script in `conf.SCRIPTS_PATH` to remote_script location, making it executable
    NOTE: assumes you are connected to a stack"""
    temporary_script = _put_temporary_script(script_filename)
    remote_sudo("mv %s %s && chmod +x %s" % (temporary_script, remote_script, remote_script))

def run_script(script_filename, *script_params, **environment_variables):
    """uploads a script for SCRIPTS_PATH and executes it in the /tmp dir with given params.
    WARN: assumes you are connected to a stack"""
    remote_script = _put_temporary_script(script_filename)

    def escape_string_parameter(parameter):
        return "'%s'" % parameter

    env_string = ['%s=%s' % (k, v) for k, v in environment_variables.items()]
    cmd = ["/bin/bash", remote_script] + lmap(escape_string_parameter, list(script_params))
    retval = remote_sudo(" ".join(env_string + cmd))
    remote_sudo("rm " + remote_script) # remove the script after executing it
    return retval

