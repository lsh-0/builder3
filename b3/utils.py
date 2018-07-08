import yaml, copy

def ensure(v, msg, ExceptionClass=AssertionError):
    if not v:
        raise ExceptionClass(msg)

def load_yaml(path):
    with open(path, 'r') as fh:
        return yaml.safe_load(fh)

def deepcopy(d):
    return copy.deepcopy(d)

def firstnn(fn, lst):
    "returns the first value in `lst` where `fn(x)` is truthy"
    for v in lst:
        if fn(v):
            return v
