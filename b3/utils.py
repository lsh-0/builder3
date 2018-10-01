from datetime import datetime
import os, sys, itertools
from os.path import join
import json, yaml, copy
from pygments import highlight
from pygments import lexers
from pygments import formatters
from functools import reduce
from fabric.api import local, lcd
from . import conf
import logging

LOG = logging.getLogger(__name__)

class BldrAssertionError(AssertionError):
    pass

def ensure(v, msg, ExceptionClass=BldrAssertionError):
    if not v:
        raise ExceptionClass(msg)

def thread(x, *fns):
    for fn in fns:
        if isinstance(fn, str):
            x = getattr(x, fn)() # call method
        else:
            x = fn(x)
    return x

def threadm(x, *fns):
    if isinstance(x, tuple):
        return tuple(thread(xn, *fns) for xn in x)
    return thread(x, *fns)

def flatten(lst):
    return list(itertools.chain(*lst))

def lmap(fn, lst):
    return list(map(fn, lst))

def lfilter(fn, lst):
    return list(filter(fn, lst))

def first(x):
    return list(x)[0]

def dictfilterv(fn, d):
    "filters given dict where fn(val) is truthy"
    return {key: val for key, val in d.items() if fn(val)}

def dictmap(fn, d):
    "maps given fn to fn(key, val)"
    return [fn(key, val) for key, val in d.items()]

def subdict(d, lst):
    return {key: val for key, val in d.items() if key in lst}

def json_unsafe_dumps(d, *args, **kwargs):
    def fn(x):
        if isinstance(x, datetime):
            return x.isoformat()
        return '[unserialisable object %r]' % x
    return json.dumps(d, *args, default=fn, **kwargs)

def cpprint(d):
    "colourised pretty printer. not safe for proper data serialisation"
    data = json_unsafe_dumps(d, indent=4)
    # why the calls to `getattr`? pylint complains about no-members
    lexer = getattr(lexers, 'Python3Lexer')()
    formatter = getattr(formatters, 'TerminalFormatter')()
    sys.stdout.write((highlight(data, lexer, formatter)))

def load_yaml(path):
    with open(path, 'r') as fh:
        return yaml.safe_load(fh)

def dump_yaml(data, path):
    with open(path, 'w') as fh:
        return yaml.safe_dump(data, fh, default_flow_style=False)

def _deepmerge(a, b):
    ta, tb = type(a), type(b)
    if ta == dict:
        # merging b into a
        ensure(tb == dict, "only a dict can be merged with a dict, not: %s" % tb)
        for key in b:
            newval = deepmerge(a.get(key), b[key])
            a[key] = newval
        return a
    elif ta == list:
        if tb == list:
            a.extend(b) # contents of b simply extend those of a
        else:
            a.append(b)
        return a
    return b # b replaces a

def deepmerge(*lst):
    return reduce(_deepmerge, lst)

def deepcopy(d):
    return copy.deepcopy(d)

def merge(d1, d2):
    d3 = deepcopy(d1)
    d3.update(d2)
    return d3

def firstnn(fn, lst):
    "returns the first value in `lst` where `fn(x)` is truthy"
    for v in lst:
        if fn(v):
            return v

def mkdirs(path):
    os.system("mkdir -p %s" % path)

def parse_iid(iid):
    return iid.split('--')

def repo_name(url):
    "git@bitbucket.org:user/reponame.git => reponame"
    return os.path.splitext(os.path.basename(url))[0]

#
#
#

def local_cmd(command, cwd=None, capture=False):
    cwd = cwd or conf.PROJECT_DIR
    with lcd(cwd):
        ret = local(command, capture)
        return {
            'rc': ret.return_code,
            'stdout': str(ret), # empty if capture=False
            'stderr': ret.stderr, # empty if capture=False
        }

def run_script(script_filename, cwd=None, params=None):
    "executes a script LOCALLY"
    cwd = cwd or conf.PROJECT_DIR
    script = os.path.abspath(join("scripts", script_filename))
    def escape_string_parameter(parameter):
        return "'%s'" % parameter
    cmd = ["/bin/bash", script] + lmap(escape_string_parameter, params) if params else []
    cmd = " ".join(cmd)
    return local_cmd(cmd, cwd)

#
#
#

def clone_repo(repo_url):
    """`repo_url` is the repository url location, something git would understand."""
    try:
        return run_script("clone-repo.sh", params=[repo_name(repo_url), repo_url])
    except BaseException:
        print('failed cloning',repo_url)
