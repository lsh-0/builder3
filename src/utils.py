import yaml
def load_yaml(path):
    with open(path, 'r') as fh:
        return yaml.safe_load(fh)
