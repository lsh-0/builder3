import os, sys, itertools
import json, yaml, copy
from pygments import highlight
from pygments import lexers
from pygments import formatters
from functools import reduce

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

def dictfilterv(fn, d):
    "filters given dict where fn(val) is truthy"
    return {key: val for key, val in d.items() if fn(val)}

def dictmap(fn, d):
    "maps given fn to fn(key, val)"
    return [fn(key, val) for key, val in d.items()]

def cpprint(d):
    "colourised pretty printer"
    data = json.dumps(d, indent=4)
    lexer = lexers.Python3Lexer()
    formatter = formatters.TerminalFormatter()
    sys.stdout.write((highlight(data, lexer, formatter)))

def load_yaml(path):
    with open(path, 'r') as fh:
        return yaml.safe_load(fh)

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
