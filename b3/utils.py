import yaml, copy

def load_yaml(path):
    with open(path, 'r') as fh:
        return yaml.safe_load(fh)

def deepcopy(d):
    return copy.deepcopy(d)
