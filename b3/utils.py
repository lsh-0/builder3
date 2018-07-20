import os, itertools
import yaml, copy

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

def flatten(lst):
    return list(itertools.chain(*lst))

def lmap(fn, lst):
    return list(map(fn, lst))

def dictfilterv(fn, d):
    "filters given dict where fn(val) is truthy"
    return {key: val for key, val in d.items() if fn(val)}

def dictmap(fn, d):
    "maps given fn to fn(key, val)"
    return [fn(key, val) for key, val in d.items()]


def load_yaml(path):
    with open(path, 'r') as fh:
        return yaml.safe_load(fh)

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
