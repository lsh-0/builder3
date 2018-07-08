from invoke import task
from b3 import project, conf
import json

def pprint(d):
    print(json.dumps(d, indent=4))

@task
def pdata(c, name):
    pprint(project.project_data(name))

@task
def defaults(c, oname=None):
    defaults, _ = project.all_project_data(oname)
    pprint(defaults)
